#import "./libs/nat.mligo" "Nat"
#import "./libs/bytes.mligo" "Bytes_utils"
#import "./libs/patricia_trie.mligo" "PatriciaTrie"

type config = [@layout:comb] {
    // Multi-sig address allowed to manage the contract
    administrator : address;
    // This constant sets how many levels each snapshot has.
    snapshot_duration : nat;
    // This constant is used to limit the data length being inserted (in bytes).
    max_state_size : nat;
}

type storage = [@layout:comb] {
  config : config;
  snapshot_start_level : nat;
  snapshot_counter : nat;
  snapshot_level : (nat, nat) big_map;
  merkle_tree : PatriciaTrie.tree;
}

type configure_action = [@layout:comb]
| Update_administrator of address
| Update_max_state_size of nat
| Update_snapshot_duration of nat

type parameter = [@layout:comb]
| Snapshot
| Insert of bytes * bytes
| Configure of configure_action list

type return = operation list * storage

module Error =
  struct
    type t = string
    let cannot_snapshot : t = "CANNOT_SNAPSHOT"
    let state_too_large : t = "STATE_TOO_LARGE"
    let proof_not_found : t = "PROOF_NOT_FOUND"
  end

(* Lambdas *)

let finalize_snapshot (required, store : bool * storage) : return =
  let store = if store.snapshot_start_level = 0n
  then
    // Start snapshot
    { store with
      snapshot_start_level = Tezos.get_level();
      merkle_tree = PatriciaTrie.empty_tree
    }
  else
    store
  in
  if store.snapshot_start_level + store.config.snapshot_duration < Tezos.get_level() && store.merkle_tree.root <> PatriciaTrie.null_hash
  then
      // Finalize & Start snapshot
      let snapshot_counter = store.snapshot_counter + 1n in
      let snapshot_start_level = Tezos.get_level() in
      let snapshot_level = is_nat (snapshot_start_level - 1) in
      let event_payload = {
        snapshot = store.snapshot_counter;
        level = snapshot_level;
      } in
      (
        [Tezos.emit "%SNAPSHOT_FINALIZED" event_payload],
        { store with
          snapshot_counter;
          snapshot_start_level;
          snapshot_level = Big_map.update (snapshot_counter : nat) snapshot_level store.snapshot_level;
          merkle_tree = PatriciaTrie.empty_tree
        }
      )
  else
    let () = assert_with_error (not required) Error.cannot_snapshot in
    ([], store)

(* Entrypoints *)

let configure (actions, store : (configure_action list) * storage) : storage =
  let apply_action (acc, action : storage * configure_action) =
    match action with
        Update_administrator (new_admin) -> { acc with
          config = {
            acc.config with administrator = new_admin
          }
        }
      | Update_max_state_size (size) -> { acc with
          config = {
            acc.config with max_state_size = size
          }
        }
      | Update_snapshot_duration (duration) -> { acc with
          config = {
            acc.config with snapshot_duration = duration
          }
        }
      in
  List.fold_left apply_action store actions

(* Include new state into the merkle tree. *)
let insert (key, value, store, finalize_snapshot, insert_at_edge : bytes * bytes * storage * ((bool * storage) -> return) * PatriciaTrie.insert_at_edge_t) : return =
  // Check and finalize snapshot
  let (ops, store) = finalize_snapshot(false, store) in
  // Do not allow users to insert values bigger than max_state_size
  let () = assert_with_error ((Bytes.length value) <= store.config.max_state_size) Error.state_too_large in

  // Set new state
  let value_hash = PatriciaTrie.hash_state(Tezos.get_sender(), key, value) in
  let store = {
    store with merkle_tree = {
      store.merkle_tree with states = Map.update (value_hash : bytes) (Some value) store.merkle_tree.states;
    }
  } in

  let label = {
    data = Nat.of_bytes(PatriciaTrie.hash_key(Tezos.get_sender(), key));
    length = PatriciaTrie.hash_length;
  } in

  let new_tree, root_edge = if store.merkle_tree.root_edge.node = PatriciaTrie.null_hash && store.merkle_tree.root_edge.label.length = 0n
  then
    // The tree is empty
    (
      store.merkle_tree,
      {
        label=label;
        node=value_hash;
      }
    )
  else
    insert_at_edge(store.merkle_tree, store.merkle_tree.root_edge, label, value_hash)
  in
  (
    ops,
    {
      store with merkle_tree = {
        new_tree with
          root = PatriciaTrie.hash_edge(root_edge);
          root_edge;
      }
    }
  )

let main (action, store : parameter * storage) : return =
  let global_finalize_snapshot = finalize_snapshot in
  let global_insert_at_edge = PatriciaTrie.insert_at_edge in
  match action with
    Snapshot -> global_finalize_snapshot(true, store)
  | Insert (key, value) -> insert(key, value, store, global_finalize_snapshot, global_insert_at_edge)
  | Configure (action) -> [], configure(action, store)

type get_proof_parameter = [@layout:comb] {
  owner: address;
  key: bytes;
}

type path_node = [@layout:comb]
| Left of bytes
| Right of bytes

type get_proof_result = [@layout:comb] {
  snapshot: nat;
  merkle_root: bytes;
  key: bytes;
  value: bytes;
  path: path_node list;
}

(* Returns the Merkle-proof for the given key. *)
[@view] let get_proof ((owner, key), store: (address * bytes) * storage) : get_proof_result =
  let label = {
    data = Nat.of_bytes(PatriciaTrie.hash_key(owner, key));
    length = PatriciaTrie.hash_length;
  } in

  let rec get_path(tree, edge, label, proof : PatriciaTrie.tree * PatriciaTrie.edge * PatriciaTrie.edge_label * path_node list): bytes * path_node list =
    let prefix, suffix = PatriciaTrie.split_common_prefix(label, edge.label) in
    // Ensure that the path exists
    let () = assert_with_error (prefix.length = edge.label.length) Error.state_too_large in

    if suffix.length = 0n
    then
        // Proof found
        let value = Option.unopt (Map.find_opt edge.node tree.states) in
        (value, proof)
    else
      let head, tail = PatriciaTrie.chop_first_bit suffix in
      // Add hash to proof path with direction (0=left or 1=right)
      //
      // For head = 0
      //
      //      h(a+b)
      //       /   \
      //    0 /     \ 1
      //   h(a)    h(b)
      //    |        |
      //   head    complement
      //
      // The proof path must include the complement, since
      // the head is already known.
      let node = Option.unopt (Map.find_opt edge.node tree.nodes) in
      let edge_hash = PatriciaTrie.hash_edge(Option.unopt (Map.find_opt (1-head) node)) in
      let path_node = if head = 0 then (Right edge_hash) else (Left edge_hash) in

      let new_edge = Option.unopt (Map.find_opt head node) in
      get_path(tree, new_edge, tail, path_node :: proof)
  in
  let value, path = get_path(store.merkle_tree, store.merkle_tree.root_edge, label, []) in
  {
    snapshot = store.snapshot_counter + 1n;
    merkle_root = store.merkle_tree.root;
    key = key;
    value;
    path;
  }


type verify_proof_argument = [@layout:comb] {
  state_root: bytes;
  owner: address;
  key: bytes;
  value: bytes;
  path: path_node list;
}

(* Validates a proof against a given state. *)
[@view] let verify_proof (param, _store: verify_proof_argument * storage) : bool =
  let derive_hash (acc, node : bytes * path_node): bytes =
    match node with
    | Left (h) ->
      PatriciaTrie.hash_function (Bytes.concat h acc)
    | Right (h) ->
      PatriciaTrie.hash_function (Bytes.concat acc h)
  in
  let value_hash = PatriciaTrie.hash_state(param.owner, param.key, param.value) in
  let derived_hash = List.fold_left derive_hash value_hash param.path in
  derived_hash = param.state_root
