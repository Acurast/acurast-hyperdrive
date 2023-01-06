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
            root = 0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563;
            root_edge = {
                label = {
                    data = 9735896544346729033258892448620499820287387749512818771246640093787233631499n ;
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
    let () = Test.set_source bob in
    let _result = Test.transfer_to_contract_exn contr (Insert (0x636f756e746573, 0x0101010101010101010101010101010101010101010101010101010101010101)) 0tez in
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
                    0x2b639e0b5097f601aeeec60e2063037fbc5980a82967535d9fb8e08520e233e4,
                    Map.literal [
                        (0, { label = { data = 2498890967014466819285705885577505579458013707910283518780541093292663029003n; length = 251n; }; node = 0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563; }) ;
                        (1, { label = { data = 259906525983640990778894440752872650209467999544635471875703360995182209290n; length = 251n; }; node = 0xcebc8882fecbec7fb80d2cf4b312bec018884c2d66667c67a90508214bd8bafc; }) ;
                    ]
                );
            ];
            root = 0x2b639e0b5097f601aeeec60e2063037fbc5980a82967535d9fb8e08520e233e4;
            root_edge = {
                label = {
                    data = 1n ;
                    length = 4n ;
                };
                node = 0x2b639e0b5097f601aeeec60e2063037fbc5980a82967535d9fb8e08520e233e4;
            };
            states = Map.literal [
                (0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563, 0x0000000000000000000000000000000000000000000000000000000000000000);
                (0xcebc8882fecbec7fb80d2cf4b312bec018884c2d66667c67a90508214bd8bafc, 0x0101010101010101010101010101010101010101010101010101010101010101);
            ]
        };
    } in
    let () = assert (Test.get_storage taddr = expected_storage) in
    let () = Test.set_source claus in
    let _result = Test.transfer_to_contract_exn contr (Insert (0x636f756e746574, 0x0202020202020202020202020202020202020202020202020202020202020202)) 0tez in
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
                    0x2b639e0b5097f601aeeec60e2063037fbc5980a82967535d9fb8e08520e233e4,
                    Map.literal [
                        (0, { label = { data = 2498890967014466819285705885577505579458013707910283518780541093292663029003n; length = 251n; }; node = 0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563; }) ;
                        (1, { label = { data = 259906525983640990778894440752872650209467999544635471875703360995182209290n; length = 251n; }; node = 0xcebc8882fecbec7fb80d2cf4b312bec018884c2d66667c67a90508214bd8bafc; }) ;
                    ]
                );
                (
                    0x5c2681f0f2af2e576d21e5b85156e2ad036ad7c9b37f2ba35fe8cdfd5dca1432,
                    Map.literal [
                        (0, { label = { data = 1n; length = 2n; }; node = 0x2b639e0b5097f601aeeec60e2063037fbc5980a82967535d9fb8e08520e233e4; }) ;
                        (1, { label = { data = 19325644539396737862298362442106058253679263789628498884142745090485904706773n; length = 254n; }; node = 0xee4a079f5b14a24465181d45af32a8053c2d446446d7019359e210b82e53b8ba; }) ;
                    ]
                );
            ];
            root = 0x5c2681f0f2af2e576d21e5b85156e2ad036ad7c9b37f2ba35fe8cdfd5dca1432;
            root_edge = {
                label = {
                    data = 0n ;
                    length = 1n ;
                };
                node = 0x5c2681f0f2af2e576d21e5b85156e2ad036ad7c9b37f2ba35fe8cdfd5dca1432;
            };
            states = Map.literal [
                (0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563, 0x0000000000000000000000000000000000000000000000000000000000000000);
                (0xcebc8882fecbec7fb80d2cf4b312bec018884c2d66667c67a90508214bd8bafc, 0x0101010101010101010101010101010101010101010101010101010101010101);
                (0xee4a079f5b14a24465181d45af32a8053c2d446446d7019359e210b82e53b8ba, 0x0202020202020202020202020202020202020202020202020202020202020202)
            ]
        };
    } in
    let () = assert (Test.get_storage taddr = expected_storage) in

    let key = 0x636f756e746574 in
    let store: IBCF_Aggregator.storage = (Test.get_storage taddr) in
    let result = Test.run IBCF_Aggregator.get_proof((claus, key), store) in
    let expected_result : IBCF_Aggregator.get_proof_result = {
        snapshot = 1n;
        merkle_root = 0x5c2681f0f2af2e576d21e5b85156e2ad036ad7c9b37f2ba35fe8cdfd5dca1432;
        key = 0x636f756e746574;
        value = 0x0202020202020202020202020202020202020202020202020202020202020202;
        proof =  [
            (Left 0x2b639e0b5097f601aeeec60e2063037fbc5980a82967535d9fb8e08520e233e4)
        ];
    } in
    let expected_result = Test.eval expected_result in
    let () = assert (result = expected_result) in

    let arg: IBCF_Aggregator.verify_proof_argument = {
        state_root = 0x5c2681f0f2af2e576d21e5b85156e2ad036ad7c9b37f2ba35fe8cdfd5dca1432;
        owner = 0x;
        key = 0x636f756e746574;
        value = 0x0202020202020202020202020202020202020202020202020202020202020202;
        proof =  [
            (Left 0x2b639e0b5097f601aeeec60e2063037fbc5980a82967535d9fb8e08520e233e4)
        ];
    } in
    let result = Test.run IBCF_Aggregator.verify_proof(arg, Test.get_storage taddr) in
    let expected_result = Test.eval true in
    assert (result = expected_result)
