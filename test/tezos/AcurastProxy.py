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

    scenario.show(sp.pack((1, "ASSIGN_JOB_PROCESSOR", sp.pack(sp.pair(1, alice.address)))))
    scenario.show(sp.pack((2, "ASSIGN_JOB_PROCESSOR", sp.pack(sp.pair(1, bob.address)))))

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
            1: sp.bytes("0xc003f0e38f6a98618786c3c02590cfbbbda715e4f5f7fb2f2988b59e82a91724")
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
                        IngoingActionKind.ASSIGN_JOB_PROCESSOR: sp.record(
                            function=IngoingActionLambda.assign_processor,
                            storage=sp.record(
                                version=1, data=sp.bytes("0x")
                            ),
                        ),
                    }
                ),
            ),
            outgoing_seq_id=0,
            ingoing_seq_id=0,
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
            proof = [],
            leaves = [
                sp.record(
                    k_index = 0,
                    mmr_pos = 0,
                    data = sp.bytes("0x05070700010707010000001441535349474e5f4a4f425f50524f434553534f520a0000002005070700010a000000160000eaeec9ada5305ad61fc452a5ee9f7d4f55f80467")
                ),
                sp.record(
                    k_index = 1,
                    mmr_pos = 1,
                    data = sp.bytes("0x05070700020707010000001441535349474e5f4a4f425f50524f434553534f520a0000002005070700010a000000160000edaa0fa299565241bd285414579f88705568c6b0")
                ),
            ],
            mmr_size = 3
        )
    )

    scenario.verify(consumer.data.config.acurast_processors.contains(alice.address))
    scenario.verify(consumer.data.config.acurast_processors.contains(bob.address))

    consumer.fulfill(sp.record(job_id=1, payload=sp.bytes("0x"))).run(sender=alice.address)
