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
                    0xc951400ac5fb3e0671caf89a957b8d920e96ae394a80d54ebf9654e22ba6c44d,
                    Map.literal [
                        (0, { label = { data = 32790450749271752764346364856143980207165848111769501219716576803845872506964n; length = 255n; }; node = 0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563; }) ;
                        (1, { label = { data = 16931444101414541351136056886748077815460697731282278637125793934784438946856n; length = 255n; }; node = 0xcebc8882fecbec7fb80d2cf4b312bec018884c2d66667c67a90508214bd8bafc; }) ;
                    ]
                );
            ];
            root = 0x06b186a4a230c8d7cf0e454e18708b011f3971810ac15661bd48815983fead7b;
            root_edge = {
                label = {
                    data = 0n ;
                    length = 0n ;
                };
                node = 0xc951400ac5fb3e0671caf89a957b8d920e96ae394a80d54ebf9654e22ba6c44d;
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
                    0x066c203ecda11321839c8142d3ae475530546886f2346d16f9e82506987a0d27,
                    Map.literal [
                        (0, { label = { data = 11681471601726813615347185484978372415613812426077372602268941237615282411783n; length = 254n; }; node = 0xee4a079f5b14a24465181d45af32a8053c2d446446d7019359e210b82e53b8ba; }) ;
                        (1, { label = { data = 3842428439942703908453618603972003243848351945359360209852180801867590096980n; length = 254n; }; node = 0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563; }) ;
                    ]
                );
                (
                    0x17400cd2c8cac24b4f8db41fe74301756f8a1d4c64a9ccb2c50bcedff516d2e3,
                    Map.literal [
                        (0, { label = { data = 0n; length = 0n; }; node = 0x066c203ecda11321839c8142d3ae475530546886f2346d16f9e82506987a0d27; }) ;
                        (1, { label = { data = 16931444101414541351136056886748077815460697731282278637125793934784438946856n; length = 255n; }; node = 0xcebc8882fecbec7fb80d2cf4b312bec018884c2d66667c67a90508214bd8bafc; }) ;
                    ]
                );
            ];
            root = 0x12783f206513edf429533b566daf2b75a45db6bcf662ad4595f5764299a286bf;
            root_edge = {
                label = {
                    data = 0n ;
                    length = 0n ;
                };
                node = 0x17400cd2c8cac24b4f8db41fe74301756f8a1d4c64a9ccb2c50bcedff516d2e3;
            };
            states = Map.literal [
                (0x290decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563, 0x0000000000000000000000000000000000000000000000000000000000000000);
                (0xcebc8882fecbec7fb80d2cf4b312bec018884c2d66667c67a90508214bd8bafc, 0x0101010101010101010101010101010101010101010101010101010101010101);
                (0xee4a079f5b14a24465181d45af32a8053c2d446446d7019359e210b82e53b8ba, 0x0202020202020202020202020202020202020202020202020202020202020202)
            ]
        };
    } in
    // let event: PatriciaTrie.edge_label list = Test.get_last_events_from taddr "TEST" in
    // let () = Test.log ("\n\nEvents:", event) in
    // let () = Test.log ("\n\n\nStorage:", (Test.get_storage taddr)) in
    assert (Test.get_storage taddr = expected_storage)
