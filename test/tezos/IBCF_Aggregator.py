import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, ENCODE, Error, EMPTY_TREE
from contracts.tezos.utils.utils import Bytes


def update_administrator(payload):
    return sp.variant("update_administrator", payload)


def update_snapshot_duration(payload):
    return sp.variant("update_snapshot_duration", payload)


def update_max_state_size(payload):
    return sp.variant("update_max_state_size", payload)


@sp.add_test(name="IBCF")
def test():
    admin = sp.test_account("admin")
    alice = sp.record(address=sp.address("tz1TDZG4vFoA2xutZMYauUnS4HVucnAGQSpZ"))
    bob = sp.record(address=sp.address("tz1KeYsjjSCLEELMuiq1oXzVZmuJrZ15W4mv"))
    claus = sp.record(address=sp.address("tz1fi3AzSELiXmvcrLKrLBUpYmq1vQGMxv9p"))

    bytes_of_string = sp.build_lambda(Bytes.of_string)
    encoded_counter_key = bytes_of_string("counter")
    encoded_counter_value_1 = bytes_of_string("1")
    encoded_counter_value_2 = bytes_of_string("2")
    encoded_counter_value_3 = bytes_of_string("3")

    BLOCK_LEVEL_1 = 1
    BLOCK_LEVEL_2 = 2

    scenario = sp.test_scenario()
    ibcf = IBCF_Aggregator()
    ibcf.update_initial_storage(
        sp.record(
            config=sp.record(
                administrator=admin.address, max_state_size=32, snapshot_duration=5
            ),
            snapshot_start_level=0,
            snapshot_counter=0,
            snapshot_level=sp.big_map(),
            merkle_tree=EMPTY_TREE,
        )
    )

    scenario += ibcf

    # Try to set alice as administrator
    ibcf.configure([update_administrator(alice.address)]).run(
        sender=alice.address, valid=False, exception=Error.NOT_ADMINISTRATOR
    )
    # Set alice as administrator
    ibcf.configure([update_administrator(alice.address)]).run(sender=admin.address)
    scenario.verify(ibcf.data.config.administrator == alice.address)
    # Revert to original administrator
    ibcf.configure([update_administrator(admin.address)]).run(sender=alice.address)
    scenario.verify(ibcf.data.config.administrator == admin.address)

    # Update history_ttl and max_state_size
    ibcf.configure([update_snapshot_duration(10), update_max_state_size(16)]).run(
        sender=admin.address,
    )
    scenario.verify(ibcf.data.config.snapshot_duration == 10)
    scenario.verify(ibcf.data.config.max_state_size == 16)
    # Revert max_state_size change
    ibcf.configure([update_max_state_size(32)]).run(
        sender=admin.address,
    )

    # Cannot snapshot before a whole snapshot cycle has passed.
    ibcf.snapshot().run(valid=False, exception=Error.CANNOT_SNAPSHOT)

    # Do not allow states bigger than 32 bytes
    ibcf.insert(
        sp.record(key=encoded_counter_key, value=sp.bytes("0x" + ("00" * 33)))
    ).run(
        sender=alice.address,
        level=BLOCK_LEVEL_1,
        valid=False,
        exception=Error.STATE_TOO_LARGE,
    )
    # states with 32 bytes or less are allowed
    ibcf.insert(
        sp.record(key=encoded_counter_key, value=sp.bytes("0x" + ("00" * 32)))
    ).run(sender=alice.address, level=BLOCK_LEVEL_1)

    # Insert multiple states
    ibcf.insert(sp.record(key=encoded_counter_key, value=encoded_counter_value_1)).run(
        sender=alice.address, level=BLOCK_LEVEL_1
    )
    ibcf.insert(sp.record(key=encoded_counter_key, value=encoded_counter_value_2)).run(
        sender=bob.address, level=BLOCK_LEVEL_1
    )
    ibcf.insert(sp.record(key=encoded_counter_key, value=encoded_counter_value_2)).run(
        sender=claus.address, level=BLOCK_LEVEL_1
    )

    # Get proof of inclusion
    proof = scenario.compute(
        ibcf.get_proof(sp.record(owner=alice.address, key=encoded_counter_key))
    )

    # Verify proof (Valid)
    scenario.verify(
        ibcf.verify_proof(
            sp.record(
                path=proof.path,
                state=sp.record(
                    owner=alice.address,
                    key=encoded_counter_key,
                    value=encoded_counter_value_1,
                ),
            )
        )
        == sp.unit
    )

    # Insert multiple new states
    ibcf.insert(sp.record(key=encoded_counter_key, value=encoded_counter_value_2)).run(
        sender=alice.address, level=BLOCK_LEVEL_2
    )
    ibcf.insert(sp.record(key=encoded_counter_key, value=encoded_counter_value_1)).run(
        sender=bob.address, level=BLOCK_LEVEL_2
    )

    # Finalize snapshot and start a new one
    scenario.verify(ibcf.data.snapshot_counter == 0)
    ibcf.insert(sp.record(key=encoded_counter_key, value=encoded_counter_value_3)).run(
        sender=claus.address, level=BLOCK_LEVEL_2 + 10
    )
    scenario.verify(ibcf.data.snapshot_counter == 1)

    # Verify old proof against a fresh snapshot (Invalid)
    ex = sp.catch_exception(
        ibcf.verify_proof(
            sp.record(
                path=proof.path,
                state=sp.record(
                    owner=alice.address,
                    key=encoded_counter_key,
                    value=encoded_counter_value_1,
                ),
            )
        ),
        t=sp.TString,
    )
    scenario.verify(ex == sp.some(Error.PROOF_INVALID))

    # Get proof of inclusion
    proof = ibcf.get_proof(sp.record(owner=claus.address, key=encoded_counter_key))

    # Cannot generate a proof for an item that does not exist
    ex = sp.catch_exception(
        ibcf.get_proof(sp.record(owner=alice.address, key=encoded_counter_key)),
        t=sp.TString,
    )
    scenario.verify(ex == sp.some(Error.PROOF_NOT_FOUND))

    # Verify proof (Valid)
    scenario.verify(
        ibcf.verify_proof(
            sp.record(
                path=proof.path,
                state=sp.record(
                    owner=claus.address,
                    key=encoded_counter_key,
                    value=encoded_counter_value_3,
                ),
            )
        )
        == sp.unit
    )

    # Cannot snapshot before a new snapshot cycle starts
    ibcf.snapshot().run(
        level=BLOCK_LEVEL_2 + 10, valid=False, exception=Error.CANNOT_SNAPSHOT
    )


@sp.add_test(name="Ensure_same_behaviour")
def test():
    admin = sp.test_account("admin")
    alice = sp.record(address=sp.address("tz1TDZG4vFoA2xutZMYauUnS4HVucnAGQSpZ"))
    bob = sp.record(address=sp.address("tz1KeYsjjSCLEELMuiq1oXzVZmuJrZ15W4mv"))
    claus = sp.record(address=sp.address("tz1fi3AzSELiXmvcrLKrLBUpYmq1vQGMxv9p"))

    encoded_alice_address = ENCODE(alice.address)
    encoded_claus_address = ENCODE(claus.address)

    bytes_of_string = sp.build_lambda(Bytes.of_string)
    encoded_counter_key = bytes_of_string("counter")
    encoded_counter_value_1 = bytes_of_string("1")
    encoded_counter_value_2 = bytes_of_string("2")
    encoded_counter_value_3 = bytes_of_string("3")

    BLOCK_LEVEL_1 = 1
    BLOCK_LEVEL_2 = 2

    scenario = sp.test_scenario()
    ibcf = IBCF_Aggregator()
    ibcf.update_initial_storage(
        sp.record(
            config=sp.record(
                administrator=admin.address, max_state_size=32, snapshot_duration=5
            ),
            snapshot_start_level=0,
            snapshot_counter=0,
            snapshot_level=sp.big_map(),
            merkle_tree=EMPTY_TREE,
        )
    )
    scenario += ibcf

    ibcf.insert(
        sp.record(
            key=sp.bytes("0x636f756e746572"),
            value=sp.bytes(
                "0x0000000000000000000000000000000000000000000000000000000000000000"
            ),
        )
    ).run(sender=alice.address, level=BLOCK_LEVEL_2)
    expected_merkle_tree = sp.record(
        root=sp.bytes(
            "0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa"
        ),
        root_edge=sp.record(
            node=sp.bytes(
                "0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa"
            ),
            label=sp.record(
                data=9735896544346729033258892448620499820287387749512818771246640093787233631499,
                length=256,
            ),
        ),
        nodes=sp.map(),
        states={
            sp.bytes(
                "0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa"
            ): sp.bytes(
                "0x0000000000000000000000000000000000000000000000000000000000000000"
            )
        },
    )
    scenario.verify_equal(ibcf.data.merkle_tree, expected_merkle_tree)
    scenario.verify(ibcf.data.snapshot_start_level == BLOCK_LEVEL_2)

    ibcf.insert(
        sp.record(
            key=sp.bytes("0x636f756e746573"),
            value=sp.bytes(
                "0x0101010101010101010101010101010101010101010101010101010101010101"
            ),
        )
    ).run(sender=bob.address, level=BLOCK_LEVEL_2)
    expected_merkle_tree = sp.record(
        root=sp.bytes(
            "0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f"
        ),
        root_edge=sp.record(
            node=sp.bytes(
                "0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f"
            ),
            label=sp.record(data=1, length=4),
        ),
        nodes={
            sp.bytes(
                "0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f"
            ): sp.record(
                children={
                    0: sp.record(
                        label=sp.record(
                            data=2498890967014466819285705885577505579458013707910283518780541093292663029003,
                            length=251,
                        ),
                        node=sp.bytes(
                            "0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa"
                        ),
                    ),
                    1: sp.record(
                        label=sp.record(
                            data=259906525983640990778894440752872650209467999544635471875703360995182209290,
                            length=251,
                        ),
                        node=sp.bytes(
                            "0x532fe658e43559b5505a8485d26bf10a496fa3d884552cbccb69e84d83cc1896"
                        ),
                    ),
                }
            )
        },
        states={
            sp.bytes(
                "0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa"
            ): sp.bytes(
                "0x0000000000000000000000000000000000000000000000000000000000000000"
            ),
            sp.bytes(
                "0x532fe658e43559b5505a8485d26bf10a496fa3d884552cbccb69e84d83cc1896"
            ): sp.bytes(
                "0x0101010101010101010101010101010101010101010101010101010101010101"
            ),
        },
    )
    scenario.verify_equal(ibcf.data.merkle_tree, expected_merkle_tree)
    ibcf.insert(
        sp.record(key=sp.bytes("0x636f756e746574"), value=sp.bytes("0x" + ("02" * 32)))
    ).run(sender=claus.address, level=BLOCK_LEVEL_2)
    expected_merkle_tree = sp.record(
        root=sp.bytes(
            "0x3ca1cde89d2ea298ece17ce0957f79080fa5f4d6365f4b7c5f6bc4b82943cb60"
        ),
        root_edge=sp.record(
            node=sp.bytes(
                "0x3ca1cde89d2ea298ece17ce0957f79080fa5f4d6365f4b7c5f6bc4b82943cb60"
            ),
            label=sp.record(data=0, length=1),
        ),
        nodes={
            sp.bytes(
                "0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f"
            ): sp.record(
                children={
                    0: sp.record(
                        label=sp.record(
                            data=2498890967014466819285705885577505579458013707910283518780541093292663029003,
                            length=251,
                        ),
                        node=sp.bytes(
                            "0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa"
                        ),
                    ),
                    1: sp.record(
                        label=sp.record(
                            data=259906525983640990778894440752872650209467999544635471875703360995182209290,
                            length=251,
                        ),
                        node=sp.bytes(
                            "0x532fe658e43559b5505a8485d26bf10a496fa3d884552cbccb69e84d83cc1896"
                        ),
                    ),
                }
            ),
            sp.bytes(
                "0x3ca1cde89d2ea298ece17ce0957f79080fa5f4d6365f4b7c5f6bc4b82943cb60"
            ): sp.record(
                children={
                    0: sp.record(
                        label=sp.record(data=1, length=2),
                        node=sp.bytes(
                            "0xc25b22ebb302fded358354f46dcec544fe1c0d4a3586f44d2cf25dd51f28007f"
                        ),
                    ),
                    1: sp.record(
                        label=sp.record(
                            data=19325644539396737862298362442106058253679263789628498884142745090485904706773,
                            length=254,
                        ),
                        node=sp.bytes(
                            "0x39da3d8e0e8d4a9b7ed1a7be853fdfda2984502f51bc32d8c9d7f89c6d67113c"
                        ),
                    ),
                }
            ),
        },
        states={
            sp.bytes(
                "0xe4c050b87ef41d180cae546ba2977ae5089db7a04a884c8d44eee1e7833efbfa"
            ): sp.bytes(
                "0x0000000000000000000000000000000000000000000000000000000000000000"
            ),
            sp.bytes(
                "0x532fe658e43559b5505a8485d26bf10a496fa3d884552cbccb69e84d83cc1896"
            ): sp.bytes(
                "0x0101010101010101010101010101010101010101010101010101010101010101"
            ),
            sp.bytes(
                "0x39da3d8e0e8d4a9b7ed1a7be853fdfda2984502f51bc32d8c9d7f89c6d67113c"
            ): sp.bytes(
                "0x0202020202020202020202020202020202020202020202020202020202020202"
            ),
        },
    )
    scenario.verify_equal(ibcf.data.merkle_tree, expected_merkle_tree)
