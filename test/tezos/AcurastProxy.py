import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, EMPTY_TREE
from contracts.tezos.AcurastProxy import AcurastProxy, ActionLambda, ActionKind, Type


def get_nonce(n):
    return sp.bytes("0x{:0>64}".format(hex(n)[2:]))


@sp.add_test(name="IBCF_Bridge")
def test():
    scenario = sp.test_scenario()

    BLOCK_LEVEL_1 = 1
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")

    aggregator = IBCF_Aggregator()
    aggregator.update_initial_storage(
        sp.record(
            config=sp.record(
                administrator=admin.address, max_state_size=512, snapshot_duration=5
            ),
            snapshot_start_level=0,
            snapshot_counter=0,
            snapshot_level=sp.big_map(),
            merkle_tree=EMPTY_TREE,
        )
    )
    scenario += aggregator

    acurastProxy = AcurastProxy()
    acurastProxy.update_initial_storage(
        sp.record(
            config=sp.record(
                governance_address=admin.address,
                merkle_aggregator=aggregator.address,
                proof_validator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
                authorized_actions=sp.big_map(
                    {
                        "REGISTER_JOB": sp.record(
                            function=ActionLambda.register_job,
                            storage=sp.record(
                                version=1, data=sp.pack(sp.record(job_id_seq=0))
                            ),
                        ),
                    }
                ),
            ),
            outgoing_counter=0,
            registry=sp.big_map(),
        )
    )
    scenario += acurastProxy

    register_job_payload = sp.set_type_expr(
        sp.record(
            destination=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            script=sp.bytes(
                "0x697066733a2f2f516d64484c6942596174626e6150645573544d4d4746574534326353414a43485937426f37414458326364446561"
            ),
            allowedSources=sp.none,
            allowOnlyVerifiedSources=True,
            schedule=sp.record(
                duration=30000,
                startTime=1678266066623,
                endTime=1678266546623,
                interval=31000,
                maxStartDelay=0,
            ),
            memory=1,
            networkRequests=1,
            storage=1,
            extra=sp.record(
                requirements=sp.record(
                    slots=1,
                    reward=sp.bytes(
                        "0x697066733a2f2f516d64484c6942596174626e6150645573544d4d4746574534326353414a43485937426f37414458326364446561"
                    ),
                    minReputation=sp.none,
                    instantMatch=sp.none,
                ),
                expectedFulfillmentFee=0,
            ),
        ),
        Type.RegisterJobAction,
    )
    register_job_action = sp.record(
        action=ActionKind.REGISTER_JOB, payload=sp.pack(register_job_payload)
    )

    acurastProxy.perform_action(register_job_action).run(
        sender=alice, level=BLOCK_LEVEL_1
    )
    acurastProxy.perform_action(register_job_action).run(
        sender=bob, level=BLOCK_LEVEL_1
    )
    acurastProxy.perform_action(register_job_action).run(
        sender=alice, level=BLOCK_LEVEL_1
    )
    acurastProxy.perform_action(register_job_action).run(
        sender=bob, level=BLOCK_LEVEL_1
    )
    acurastProxy.perform_action(register_job_action).run(
        sender=alice, level=BLOCK_LEVEL_1
    )
    acurastProxy.perform_action(register_job_action).run(
        sender=bob, level=BLOCK_LEVEL_1
    )

    # Get proof of inclusion
    proof = scenario.compute(
        aggregator.get_proof(sp.record(owner=acurastProxy.address, key=sp.pack(2)))
    )

    scenario.show(proof)
