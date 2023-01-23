#import "../../../contracts/tezos/ligo/IBCF_Aggregator.mligo" "IBCF_Aggregator"
#import "../../../contracts/tezos/ligo/libs/patricia_trie.mligo" "PatriciaTrie"

let test =
    let () = Test.reset_state 10n ([] : tez list) in
    let admin = Test.nth_bootstrap_account 0 in
    let alice = Test.nth_bootstrap_account 1 in
    let bob = Test.nth_bootstrap_account 2 in
    let claus = Test.nth_bootstrap_account 3 in
    let () = Test.log ("Admin address:", admin) in
    let () = Test.log ("Alice address:", alice) in
    let () = Test.log ("Bob address:", bob) in
    let () = Test.log ("Claus address:", claus) in

    let initial_storage : IBCF_Aggregator.storage = {
        config = {
            administrator=admin;
            max_state_size=32n;
            snapshot_duration=5n;
        };
        snapshot_start_level=0n;
        snapshot_counter=0n;
        snapshot_level=Big_map.empty;
        merkle_tree=PatriciaTrie.empty_tree;
    } in
    let taddr, _, _ = Test.originate IBCF_Aggregator.main initial_storage 0tez in

    let contr = Test.to_contract taddr in
    let () = Test.set_source alice in
    let _ = Test.transfer_to_contract_exn contr (Insert (0x636f756e746572, 0x0000000000000000000000000000000000000000000000000000000000000000)) 0tez in
    let expected_storage: IBCF_Aggregator.storage = {
        config = {
            administrator = admin;
            max_state_size = 32n;
            snapshot_duration = 5n;
        };
        snapshot_counter = 0n;
        snapshot_level = Big_map.empty;
        snapshot_start_level = 2n;
        merkle_tree = {
            nodes = Map.empty;
            root = 0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa;
            root_edge = {
                label = {
                    data = 9735896544346729033258892448620499820287387749512818771246640093787233631499n ;
                    length = 256n
                };
                node = 0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa;
            };
            states = Map.literal [
                (0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa, 0x0000000000000000000000000000000000000000000000000000000000000000);
            ]
        };
    } in
    let () = assert (Test.get_storage taddr = expected_storage) in
    let () = Test.set_source bob in
    let _ = Test.transfer_to_contract_exn contr (Insert (0x636f756e746573, 0x0101010101010101010101010101010101010101010101010101010101010101)) 0tez in
        let expected_storage: IBCF_Aggregator.storage = {
        config = {
            administrator = admin;
            max_state_size = 32n;
            snapshot_duration = 5n;
        };
        snapshot_counter = 0n;
        snapshot_level = Big_map.empty;
        snapshot_start_level = 2n;
        merkle_tree = {
            nodes = Map.literal [
                (
                    0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f,
                    Map.literal [
                        (0, { label = { data = 2498890967014466819285705885577505579458013707910283518780541093292663029003n; length = 251n; }; node = 0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa; }) ;
                        (1, { label = { data = 259906525983640990778894440752872650209467999544635471875703360995182209290n; length = 251n; }; node = 0x532fe658e43559b5505a8485d26bf10a496fa3d884552cbccb69e84d83cc1896; }) ;
                    ]
                );
            ];
            root = 0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f;
            root_edge = {
                label = {
                    data = 1n ;
                    length = 4n ;
                };
                node = 0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f;
            };
            states = Map.literal [
                (0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa, 0x0000000000000000000000000000000000000000000000000000000000000000);
                (0x532fe658e43559b5505a8485d26bf10a496fa3d884552cbccb69e84d83cc1896, 0x0101010101010101010101010101010101010101010101010101010101010101);
            ]
        };
    } in
    let () = assert (Test.get_storage taddr = expected_storage) in
    let () = Test.set_source claus in
    let _ = Test.transfer_to_contract_exn contr (Insert (0x636f756e746574, 0x0202020202020202020202020202020202020202020202020202020202020202)) 0tez in
    let expected_storage: IBCF_Aggregator.storage = {
        config = {
            administrator = admin;
            max_state_size = 32n;
            snapshot_duration = 5n;
        };
        snapshot_counter = 0n;
        snapshot_level = Big_map.empty;
        snapshot_start_level = 2n;
        merkle_tree = {
            nodes = Map.literal [
                (
                    0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f,
                    Map.literal [
                        (0, { label = { data = 2498890967014466819285705885577505579458013707910283518780541093292663029003n; length = 251n; }; node = 0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa; }) ;
                        (1, { label = { data = 259906525983640990778894440752872650209467999544635471875703360995182209290n; length = 251n; }; node = 0x532fe658e43559b5505a8485d26bf10a496fa3d884552cbccb69e84d83cc1896; }) ;
                    ]
                );
                (
                    0x3ca1cde89d2ea298ece17ce0957f79080fa5f4d6365f4b7c5f6bc4b82943cb60,
                    Map.literal [
                        (0, { label = { data = 1n; length = 2n; }; node = 0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f; }) ;
                        (1, { label = { data = 19325644539396737862298362442106058253679263789628498884142745090485904706773n; length = 254n; }; node = 0x39da3d8e0e8d4a9b7ed1a7be853fdfda2984502f51bc32d8c9d7f89c6d67113c; }) ;
                    ]
                );
            ];
            root = 0x3ca1cde89d2ea298ece17ce0957f79080fa5f4d6365f4b7c5f6bc4b82943cb60;
            root_edge = {
                label = {
                    data = 0n ;
                    length = 1n ;
                };
                node = 0x3ca1cde89d2ea298ece17ce0957f79080fa5f4d6365f4b7c5f6bc4b82943cb60;
            };
            states = Map.literal [
                (0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa, 0x0000000000000000000000000000000000000000000000000000000000000000);
                (0x532fe658e43559b5505a8485d26bf10a496fa3d884552cbccb69e84d83cc1896, 0x0101010101010101010101010101010101010101010101010101010101010101);
                (0x39da3d8e0e8d4a9b7ed1a7be853fdfda2984502f51bc32d8c9d7f89c6d67113c, 0x0202020202020202020202020202020202020202020202020202020202020202);
            ]
        };
    } in
    let () = assert (Test.get_storage taddr = expected_storage) in

    let key = 0x636f756e746574 in
    let store: IBCF_Aggregator.storage = (Test.get_storage taddr) in
    let result = Test.run IBCF_Aggregator.get_proof((claus, key), store) in
    let expected_result : IBCF_Aggregator.get_proof_result = {
        snapshot = 1n;
        merkle_root = 0x3ca1cde89d2ea298ece17ce0957f79080fa5f4d6365f4b7c5f6bc4b82943cb60;
        key = 0x636f756e746574;
        value = 0x0202020202020202020202020202020202020202020202020202020202020202;
        path =  [
            (Left 0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f)
        ];
    } in
    let expected_result = Test.eval expected_result in
    let () = assert (result = expected_result) in

    let arg: IBCF_Aggregator.verify_proof_argument = {
        state_root = 0x3ca1cde89d2ea298ece17ce0957f79080fa5f4d6365f4b7c5f6bc4b82943cb60;
        owner = claus;
        key = 0x636f756e746574;
        value = 0x0202020202020202020202020202020202020202020202020202020202020202;
        path =  [
            (Left 0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f)
        ];
    } in
    let result = Test.run IBCF_Aggregator.verify_proof(arg, Test.get_storage taddr) in
    let expected_result = Test.eval true in
    assert (result = expected_result)
