import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, EMPTY_TREE
from contracts.tezos.AcurastProxy import AcurastProxy, OutgoingActionLambda, IngoingActionLambda, OutgoingActionKind, IngoingActionKind, Type
from contracts.tezos.AcurastConsumer import AcurastConsumer
from contracts.tezos.MMR_Validator import MMR_Validator


def get_nonce(n):
    return sp.bytes("0x{:0>64}".format(hex(n)[2:]))


@sp.add_test(name="AcurastProxy")
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

    validator = MMR_Validator()
    validator.update_initial_storage(
        config=sp.record(
            governance_address=admin.address,
            validators=sp.set([alice.address, bob.address]),
            minimum_endorsements=2,
        ),
        current_snapshot=2,
        snapshot_submissions=sp.map(),
        root=sp.big_map({
            1: sp.bytes("0xf9ff75def54e55e0e7267f360278c6ced1afc8e5aa3c7ccdbdea92104898642c")
        }),
    )
    scenario += validator

    acurastProxy = AcurastProxy()
    acurastProxy.update_initial_storage(
        sp.record(
            config=sp.record(
                governance_address=admin.address,
                merkle_aggregator=aggregator.address,
                proof_validator=validator.address,
                outgoing_actions=sp.big_map(
                    {
                        OutgoingActionKind.REGISTER_JOB: sp.record(
                            function=OutgoingActionLambda.register_job,
                            storage=sp.record(
                                version=1, data=sp.pack(sp.record(job_id_seq=0))
                            ),
                        ),
                    }
                ),
                ingoing_actions=sp.big_map(
                    {
                        IngoingActionKind.ASSIGN: sp.record(
                            function=IngoingActionLambda.assign_processor,
                            storage=sp.record(
                                version=1, data=sp.bytes("0x")
                            ),
                        ),
                    }
                ),
            ),
            outgoing_seq_id=0,
            ingoing_seq_id=4,
            job_destination = sp.big_map(),
        )
    )
    scenario += acurastProxy

    consumer = AcurastConsumer()
    consumer.update_initial_storage(
        sp.record(
            config=sp.record(
                job_id=sp.none,
                acurast_proxy=acurastProxy.address,
                acurast_processors=sp.set()
            )
        )
    )
    scenario += consumer

    register_job_payload = sp.set_type_expr(
        sp.record(
            destination=consumer.address,
            script=sp.bytes(
                "0x697066733a2f2f516d64484c6942596174626e6150645573544d4d4746574534326353414a43485937426f37414458326364446561"
            ),
            allowedSources=sp.some(sp.set([sp.bytes("0x" + "00"*32)])),
            allowOnlyVerifiedSources=True,
            requiredModules=sp.set([
                0
            ]),
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
                        "0xff"
                    ),
                    minReputation=sp.none,
                    instantMatch=sp.some(sp.set([sp.record(source=sp.bytes("0x" + "11"*32), startDelay=0)])),
                ),
                expectedFulfillmentFee=0,
            ),
        ),
        Type.RegisterJobAction,
    )
    scenario.show(sp.pack(register_job_payload))
    scenario.show(sp.pack(sp.record(a=1)))
    register_job_action = sp.record(
        kind=OutgoingActionKind.REGISTER_JOB, payload=sp.pack(register_job_payload)
    )

    acurastProxy.send_actions(
        [
            register_job_action
        ]
    ).run(
        sender=alice, level=BLOCK_LEVEL_1
    )

    scenario.verify(consumer.data.config.job_id == sp.some(1))

    # Get proof of inclusion
    proof = scenario.compute(
        aggregator.get_proof(sp.record(owner=acurastProxy.address, key=sp.pack(1)))
    )

    scenario.show(proof)

    acurastProxy.receive_actions(
        sp.record(
            snapshot = 1,
            proof = [
                sp.bytes("0x53db3d426fa99eff2cc6ef1f07a226c2e5b32d9ccc2b67411d52e8d2b0de8d13"),
                sp.bytes("0xbca5ce83486f6bd8be90523d0e9bcefd812fbd451337b584d32f8203dbf340c7"),
            ],
            leaves = [
                sp.record(
                    k_index = 1,
                    mmr_pos = 8,
                    data = sp.bytes("0x05070700050707010000000641535349474e0a000000460507070a000000100000000000000000000000000000000502000000290a00000024747a316834457347756e48325565315432754e73386d664b5a38585a6f516a693348634b")
                ),
                sp.record(
                    k_index = 0,
                    mmr_pos = 10,
                    data = sp.bytes("0x05070700060707010000000641535349474e0a000000460507070a000000100000000000000000000000000000000602000000290a00000024747a316834457347756e48325565315432754e73386d664b5a38585a6f516a693348634b")
                ),
            ],
            mmr_size = 11
        )
    )


    acurastProxy.fulfill(sp.record(job_id=1, payload=sp.bytes("0x")))
