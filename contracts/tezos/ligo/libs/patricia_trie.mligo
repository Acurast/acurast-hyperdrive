#import "./bytes.mligo" "Bytes_utils"

type edge_label = {
  data : nat;
  length : nat;
}

type edge = {
  node : bytes;
  label : edge_label;
}

type node = (int, edge) map

type tree = [@layout:comb] {
  root: bytes;
  root_edge : edge;
  nodes : (bytes, node) map;
  states : (bytes, bytes) map;
}

module Error =
  struct
    type t = string
    let key_length_mismatch : t = "KEY_LENGTH_MISMATCH"
  end

let hash_length = 256n
let hash_function (b: bytes) : bytes = Crypto.keccak b
let null_hash : bytes = 0x
let empty_tree : tree = {
  root = null_hash;
  root_edge = {
        node= null_hash;
        label = {
          data = 0n;
          length = 0n;
        }
  };
  nodes = Map.empty;
  states = Map.empty;
}

[@inline] let hash_key (owner, key : address * bytes) = hash_function (Bytes.concat (Bytes.pack owner) key)

[@inline] let hash_state (owner, key, value: address * bytes * bytes) = hash_function (Bytes_utils.concat [(Bytes.pack owner); key; value])

[@inline] let hash_edge (e : edge) =
    //let encoded_length = Bytes_utils.pad_start((Bytes_utils.of_nat e.label.length), 0x00, 32n)in
    //let encoded_data = Bytes_utils.pad_start((Bytes_utils.of_nat e.label.data), 0x00, 32n)in
    //hash_function (Bytes_utils.concat [e.node ; encoded_length ; encoded_data])
    e.node

[@inline] let hash_node (node : (int, edge) map) = hash_function (Bytes.concat (hash_edge(Option.unopt (Map.find_opt 0 node))) (hash_edge(Option.unopt (Map.find_opt 1 node))))

[@inline] let get_suffix (b, length : nat * nat): nat =
    Bitwise.and b (Option.unopt (is_nat ((Bitwise.shift_left 1n length) - 1)))

[@inline] let get_prefix (b, full_length, prefix_length : nat * nat * nat): nat =
    Bitwise.shift_right b (Option.unopt (is_nat (full_length - prefix_length)))

(* Builds a pair that has as first element the first bit of a key and as second element a new key without that first bit. *)
[@inline] let chop_first_bit(key : edge_label): int * edge_label =
    let () = assert_with_error (key.length > 0n) "Null key" in

    let tail_length = abs(key.length - 1) in  // Safe to use abs, already validated above
    let tail = get_suffix(key.data, tail_length) in
    let first_bit = int(Bitwise.shift_right key.data tail_length) in

    (first_bit, { length=tail_length; data=tail; })

(* Returns a new label after removing a given `prefix_length`. *)
let remove_prefix(label, prefix_length : edge_label * nat) : edge_label =
    let () = assert_with_error (prefix_length <= label.length) "PREFIX_TOO_LONG" in
    let length = Option.unopt (is_nat (label.length - prefix_length)) in
    {
        data = get_suffix(label.data, length);
        length;
    }

// Splits the label at the given position and returns prefix and suffix,
// i.e. prefix.length == pos and prefix.data . suffix.data == l.data.
let split_at (label, position : edge_label * nat) : edge_label * edge_label =
    // The key length must be bigger or equal to the edge label length.
    let () = assert_with_error (position <= label.length && position <= 256n) "Bad position" in
    let prefix = if position = 0n
    then
        {
            data = 0n;
            length = 0n;
        }
    else
        {
            data = get_prefix(label.data, label.length, position);
            length = position;
        }
    in
    let suffix_length = Option.unopt (is_nat (label.length - position)) in
    (
        prefix,
        {
            data = get_suffix(label.data, suffix_length);
            length = suffix_length;
        }
    )

(* Returns the length of the longest common prefix of the two keys. *)
let common_prefix (a, b: edge_label * edge_label): nat =
    let rec find_common_prefix (a, b, max_length, len : edge_label * edge_label * nat * nat) : nat =
        if len < max_length
        then
            let bit_a = get_prefix(a.data, a.length, len + 1n) in
            let bit_b = get_prefix(b.data, b.length, len + 1n) in
            if bit_a = bit_b then find_common_prefix(a, b, max_length, len + 1n) else len
        else
            len
    in
    let max_length = if (a.length < b.length) then a.length else b.length in

    find_common_prefix(a, b, max_length, 0n)

(* Returns a label containing the longest common prefix of `check` and `label` and a label consisting of the remaining part of `label`. *)
let split_common_prefix(label, check : edge_label * edge_label): edge_label * edge_label =
    split_at(label, common_prefix(check, label))

let insert_node(tree, node : tree * node) : tree * bytes =
    let node_hash = hash_node node in
    let new_tree = {
        tree with nodes = Map.add node_hash node tree.nodes
    } in
    (new_tree, node_hash)

let replace_node(tree, old_hash, node: tree * bytes * node) : tree * bytes =
    let new_tree = {
        tree with nodes = Map.remove old_hash tree.nodes
    } in
    insert_node(new_tree, node)

type insert_at_edge_t = (tree * edge * edge_label * bytes) -> tree * edge
let rec insert_at_edge (tree, edge, key, value : tree * edge * edge_label * bytes) : tree * edge =
    // The key length must be bigger or equal to the edge lable length.
    let () = assert_with_error (key.length >= edge.label.length) Error.key_length_mismatch in
    let prefix, suffix = split_common_prefix(key, edge.label) in
    let new_tree, new_node_hash = if suffix.length = 0n
    then
        // Full match with the key, update operation
        (tree, value)
    else
        let head, tail = chop_first_bit(suffix) in
        if prefix.length >= edge.label.length
        then
            // Partial match, just follow the path
            let () = assert_with_error (suffix.length > 1n) "BAD_KEY" in
            match Map.find_opt edge.node tree.nodes with
            Some node ->
                let node_children = Option.unopt (Map.find_opt head node) in
                let new_tree, new_edge = insert_at_edge(tree, node_children, tail, value) in
                let new_node = Map.update head (Some new_edge) node in
                replace_node(new_tree, edge.node, new_node)
            | None -> failwith "Node does not exist."
        else
            // Mismatch, so let us create a new branch node.
            let new_node : node = Map.literal [
                (head, { node = value; label = tail; });
                (1 - head, { node = edge.node; label = remove_prefix(edge.label,  prefix.length + 1n); })
            ] in
            insert_node(tree, new_node)
    in
    let new_edge = {
        node = new_node_hash;
        label = prefix;
    } in
    (new_tree, new_edge)
