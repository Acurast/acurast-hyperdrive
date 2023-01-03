#import "../../../contracts/tezos/ligo/IBCF_Aggregator.mligo" "IBCF_Aggregator"
#import "../../../contracts/tezos/ligo/utils/patricia_trie.mligo" "PatriciaTrie"

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
    let _result = Test.transfer_to_contract_exn contr (Insert (0x636f756e746572, 0x0000000000000000000000000000000000000000000000000000000000000000)) 0tez in
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
            root = 0x263716e496734c74d0a15625b500285c704caa3b1763cd1d3f6710542dcf5015;
            root_edge = {
                label = {
                    data = 32790450749271752764346364856143980207165848111769501219716576803845872506964n ;
                    length = 256n
                };
                node = 0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563;
            };
            states = Map.literal [
                (0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563, 0x0000000000000000000000000000000000000000000000000000000000000000);
            ]
        };
    } in
    let () = assert (Test.get_storage taddr = expected_storage) in
    let () = Test.log ("\n\nStorage:", (Test.get_storage taddr)) in
    let () = Test.set_source bob in
    let _result = Test.transfer_to_contract_exn contr (Insert (0x636f756e746573, 0x0101010101010101010101010101010101010101010101010101010101010101)) 0tez in
    let () = Test.log ("\n\n\nStorage:", (Test.get_storage taddr)) in
    let () = Test.set_source claus in
    let _result = Test.transfer_to_contract_exn contr (Insert (0x636f756e746572, 0x0202020202020202020202020202020202020202020202020202020202020202)) 0tez in
    let _expected_storage: IBCF_Aggregator.storage = {
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
                    0x3cb4fe8553c0188c3efee7fbabcfd867300437aa334223786d4fe5f70a76d251,
                    Map.literal [
                        (0, { label = { data = 0n; length = 2n; }; node = 0x7f7b10713f84a7a89bb0dee1fc968730f3f92464d3c306be54a368077b094ff5; }) ;
                        (1, { label = { data = 11256624495830773423085241338917685180153310860853827273025248816129369717841n; length = 254n; }; node = 0xcaa2e77c803e03c7a95ab1feea5d897b182f0e4c7a34a832d9dd7aeb0b0df122; }) ;
                    ]
                );
                (
                    0x7f7b10713f84a7a89bb0dee1fc968730f3f92464d3c306be54a368077b094ff5,
                    Map.literal [
                        (0, { label = { data = 524346015233897943336118498891525704041206848753928406055688351376202353278n; length = 251n; }; node = 0x1ca7648000a89e7134a191c3850e70eda88c2aa349651c1e8be65a0f8eddacf8; }) ;
                        (1, { label = { data = 524346015233897943336118498891525704041206848753928406055688351376202353278n; length = 251n; }; node = 0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa; }) ;
                    ]
                );
            ];
            root = 0x3cb4fe8553c0188c3efee7fbabcfd867300437aa334223786d4fe5f70a76d251;
            root_edge = {
                label = {
                    data = 0n ;
                    length = 1n
                };
                node = 0x3cb4fe8553c0188c3efee7fbabcfd867300437aa334223786d4fe5f70a76d251;
            };
            states = Map.literal [
                (0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa, 0x0000000000000000000000000000000000000000000000000000000000000000);
                (0xcaa2e77c803e03c7a95ab1feea5d897b182f0e4c7a34a832d9dd7aeb0b0df122, 0x0101010101010101010101010101010101010101010101010101010101010101);
                (0x1ca7648000a89e7134a191c3850e70eda88c2aa349651c1e8be65a0f8eddacf8, 0x0202020202020202020202020202020202020202020202020202020202020202)
            ]
        };
    } in
    Test.log ("Storage:", (Test.get_storage taddr))
