
type edge = {
  node : bytes;
  key : {
    data : nat;
    length : nat;
  }
}

type tree = {
  root: bytes;
  root_edge : edge;
  nodes : (bytes, (int, edge) map) map;
  states : (bytes, bytes) map;
}

type config = {
    // Multi-sig address allowed to manage the contract
    administrator : address;
    // This constant sets how many levels each snapshot has.
    snapshot_duration : nat;
    // This constant is used to limit the data length being inserted (in bytes).
    max_state_size : nat;
}

type storage = {
  config : config;
  snapshot_start_level : nat;
  snapshot_counter : nat;
  snapshot_level : (nat, nat) big_map;
  merkle_tree : tree;
}

type parameter =
  Snapshot
| Insert of int
| Configure

type return = operation list * storage

(* Main access point that dispatches to the entrypoints according to
   the smart contract parameter. *)

let main (action, store : parameter * storage) : return =
 ([] : operation list),    // No operations
 (match action with
   Snapshot -> store
 | Insert (_n) -> store
 | Configure  -> store)
