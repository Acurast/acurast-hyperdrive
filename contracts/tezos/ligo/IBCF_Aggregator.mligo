
type edge = {
  node : bytes;
  key : {
    data : nat;
    length : nat;
  }
}

type tree = [@layout:comb] {
  root: bytes;
  root_edge : edge;
  nodes : (bytes, (int, edge) map) map;
  states : (bytes, bytes) map;
}

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
  merkle_tree : tree;
}

type configure_parameter =
  Update_administrator of address
| Update_snapshot_duration of nat
| Update_max_state_size of nat

type parameter =
  Snapshot
| Insert of int
| Configure of configure_parameter

type return = operation list * storage

module Error =
  struct
    type t = string
    let cannot_snapshot : t = "CANNOT_SNAPSHOT"
  end

let null_hash : bytes = 0x
let empty_tree : tree = {
  root = null_hash;
  root_edge = {
        node= null_hash;
        key = {
          data = 0n;
          length = 0n;
        }
  };
  nodes = Map.empty;
  states = Map.empty;
}

(* Lambdas *)

let finalize_snapshot (required, store : bool * storage) : return =
  let store = if store.snapshot_start_level = 0n
  then
    // Start snapshot
    { store with
      snapshot_start_level = Tezos.get_level();
      merkle_tree = empty_tree
    }
  else
    store
  in
  if store.snapshot_start_level + store.config.snapshot_duration < Tezos.get_level() && store.merkle_tree.root <> null_hash
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
          merkle_tree = empty_tree
        }
      )
  else
    let () = assert_with_error (not required) Error.cannot_snapshot in
    ([], store)

(* Entrypoints *)

let configure (action, store : configure_parameter * storage) : storage =
  match action with
    Update_administrator (new_admin) -> { store with
      config = {
        store.config with administrator = new_admin
      }
    }
  | Update_snapshot_duration (duration) -> { store with
      config = {
        store.config with snapshot_duration = duration
      }
    }
  | Update_max_state_size (size) -> { store with
      config = {
        store.config with max_state_size = size
      }
    }

let main (action, store : parameter * storage) : return =
 let global_finalize_snapshot = finalize_snapshot in
 match action with
   Snapshot -> global_finalize_snapshot(true, store)
 | Insert (_n) -> ([] : operation list), store
 | Configure (action) -> [], configure(action, store)
