#import "../../../../contracts/tezos/ligo/libs/patricia_trie.mligo" "PatriciaTrie"

let test_common_prefix =
    let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 15n; length = 4n; }, { data = 7n; length = 3n; }) in
    let result = Test.run PatriciaTrie.common_prefix input in
    let expected_result = Test.eval 3n in
    let () = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 7n; length = 3n; }, { data = 15n; length = 4n; }) in
    let result = Test.run PatriciaTrie.common_prefix input in
    let expected_result = Test.eval 3n in
    let () = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 32790450749271752764346364856143980207165848111769501219716576803845872506964n; length = 256n; }, { data = 74827488720072639062921549391092031742095690064102560656854585938741003766824n; length = 256n; }) in
    let result = Test.run PatriciaTrie.common_prefix input in
    let expected_result = Test.eval 0n in
    let () = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 10548592n; length = 24n; }, { data = 43981n; length = 16n; }) in
    let result = Test.run PatriciaTrie.common_prefix input in
    let expected_result = Test.eval 4n in
    assert (Test.michelson_equal result expected_result)

let test_split_common_prefix =
    let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 15n; length = 4n; }, { data = 7n; length = 3n; }) in
    let result = Test.run PatriciaTrie.split_common_prefix input in
    let expected_result = Test.eval ({ data = 7n; length = 3n; }, { data = 1n; length = 1n; }) in
    let () = assert (Test.michelson_equal result expected_result) in
    let input : PatriciaTrie.edge_label * PatriciaTrie.edge_label = ({ data = 10548592n; length = 24n; }, { data = 43981n; length = 16n; }) in
    let result = Test.run PatriciaTrie.split_common_prefix input in
    let expected_result = Test.eval ({ data = 10n; length = 4n; }, { data = 62832n; length = 20n; }) in
    assert (Test.michelson_equal result expected_result)

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
    let expected_result = Test.eval 0xd5f22674b860adcaf76d66ef9bcf7d5465f73928e366e000e9fc97c207e0c18f in
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
    let () = assert (Test.michelson_equal result expected_result) in
    let result = Test.run PatriciaTrie.get_prefix (32790450749271752764346364856143980207165848111769501219716576803845872506964n, 256n, 1n)  in
    let expected_result = Test.eval 0n in
    let () = assert (Test.michelson_equal result expected_result) in
    let result = Test.run PatriciaTrie.get_prefix (74827488720072639062921549391092031742095690064102560656854585938741003766824n, 256n, 1n)  in
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
