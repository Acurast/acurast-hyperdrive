#import "./utils/nat.mligo" "Nat"
#import "./utils/bytes.mligo" "Bytes_utils"
#import "./utils/patricia_trie.mligo" "PatriciaTrie"

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
      let event_payload = {
        snapshot = store.snapshot_counter;
        level = Tezos.get_level();
      } in
      (
        [Tezos.emit "%SNAPSHOT_FINALIZED" event_payload],
        { store with
          snapshot_counter;
          snapshot_start_level;
          snapshot_level = Big_map.update (snapshot_counter : nat) (is_nat (snapshot_start_level - 1)) store.snapshot_level;
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
  let value_hash = PatriciaTrie.hash_function value in
  let store = {
    store with merkle_tree = {
      store.merkle_tree with states = Map.update (value_hash : bytes) (Some value) store.merkle_tree.states;
    }
  } in

  let label = {
    data = Nat.of_bytes(PatriciaTrie.hash_function(key));
    // TODO : data = Nat.of_bytes(PatriciaTrie.hash_key(Tezos.get_sender(), key));
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

type get_proof_result = [@layout:comb] {
  snapshot: nat;
  merkle_root: bytes;
  key: bytes;
  value: bytes;
  proof: (Left of bytes | Right of bytes) list;
}


(* Returns the Merkle-proof for the given key. *)
[@view] let get_proof (param, store: get_proof_parameter * storage) : get_proof_result =
  (* TODO *)
  {
    snapshot = store.snapshot_counter + 1n;
    merkle_root = 0x00;
    key = param.key;
    value = 0x00;
    proof = [];
  }
