#import "../../../../contracts/tezos/ligo/utils/patricia_trie.mligo" "PatriciaTrie"

let test_common_prefix =
    let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 15n; length = 4n; }, { data = 7n; length = 3n; }) in
    let result = Test.run PatriciaTrie.common_prefix input in
    let expected_result = Test.eval 3n in
    let () = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 7n; length = 3n; }, { data = 15n; length = 4n; }) in
    let result = Test.run PatriciaTrie.common_prefix input in
    let expected_result = Test.eval 3n in
    assert (Test.michelson_equal result expected_result)

// let test_split_common_prefix =
//     let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 15n; length = 4n; }, { data = 7n; length = 3n; }) in
//     let result = Test.run PatriciaTrie.split_common_prefix input in
//     let expected_result = Test.eval ({ data = 7n; length = 3n; }, { data = 1n; length = 1n; }) in
//     let () = assert (Test.michelson_equal result expected_result) in
//     let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 10548592n; length = 20n; }, { data = 43981n; length = 16n; }) in
//     let result = Test.run PatriciaTrie.split_common_prefix input in
//     let expected_result = Test.eval ({ data = 160n; length = 4n; }, { data = 62832n; length = 16n; }) in
//     let () = Test.log ("Result:", result) in
//     assert (Test.michelson_equal result expected_result)

let test_chop_first_bit =
    let input : PatriciaTrie.edge_label = { data = 14n; length = 4n; } in
    let result = Test.run PatriciaTrie.chop_first_bit input in
    let expected_result = Test.eval  (1, { data = 6n; length = 3n; })  in
    let _ = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label = { data = 6n; length = 3n; } in
    let result = Test.run PatriciaTrie.chop_first_bit input in
    let expected_result = Test.eval  (1, { data = 2n; length = 2n; })  in
    let _ = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label = { data = 2n; length = 2n; } in
    let result = Test.run PatriciaTrie.chop_first_bit input in
    let expected_result = Test.eval  (1, { data = 0n; length = 1n; })  in
    let _ = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label = { data = 0n; length = 1n; } in
    let result = Test.run PatriciaTrie.chop_first_bit input in
    let expected_result = Test.eval  (0, { data = 0n; length = 0n; })  in
    assert (Test.michelson_equal result expected_result)

let test_hash_edge =
    let input : PatriciaTrie.edge = {
        node = 0xd5f22674b860adcaf76d66ef9bcf7d5465f73928e366e000e9fc97c207e0c18f;
        label = { data = 96770479151044334212888682484935290825755157000393274649179700799961558991247n; length = 256n; }
    } in
    let result = Test.run PatriciaTrie.hash_edge input in
    let expected_result = Test.eval 0x6df4fb9fbef96decc3b9cd5057ab6230edcea7e22efc6f4833db44184dd93958 in
    assert (Test.michelson_equal result expected_result)

let test_get_prefix =
    let result = Test.run PatriciaTrie.get_prefix (15n, 4n, 1n)  in
    let expected_result = Test.eval 1n in
    let () = assert (Test.michelson_equal result expected_result) in
    let result = Test.run PatriciaTrie.get_prefix (1n, 2n, 1n)  in
    let expected_result = Test.eval 0n in
    let () = assert (Test.michelson_equal result expected_result) in
    let result = Test.run PatriciaTrie.get_prefix (1n, 2n, 2n)  in
    let expected_result = Test.eval 1n in
    assert (Test.michelson_equal result expected_result)

let test_split_at =
    let input : PatriciaTrie.edge_label * nat = ({ data = 43981n; length = 16n; }, 0n) in
    let result = Test.run PatriciaTrie.split_at input  in
    let expected_result = Test.eval ({ data = 0n; length = 0n; }, { data = 43981n; length = 16n; }) in
    let () = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label * nat = ({ data = 43981n; length = 16n; }, 4n) in
    let result = Test.run PatriciaTrie.split_at input  in
    let expected_result = Test.eval ({ data = 10n; length = 4n; }, { data = 3021n; length = 12n; }) in
    assert (Test.michelson_equal result expected_result)
