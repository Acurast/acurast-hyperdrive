import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, EMPTY_TREE
from contracts.tezos.AcurastProxy import (
    AcurastProxy,
    OutgoingActionLambda,
    IngoingActionLambda,
    OutgoingActionKind,
    IngoingActionKind,
    Type,
    Inlined as AcurastProxyInlined,
    Acurast_Token_Interface,
)
from contracts.tezos.AcurastConsumer import AcurastConsumer
from contracts.tezos.MMR_Validator import MMR_Validator


class AcurastTokenInterface(sp.Contract):
    @sp.entrypoint()
    def burn_tokens(self, arg):
        sp.set_type(arg, Acurast_Token_Interface.BurnMintTokens)
        pass

    @sp.entrypoint()
    def mint_tokens(self, arg):
        sp.set_type(arg, Acurast_Token_Interface.BurnMintTokens)
        pass


class ImplicitInterface(sp.Contract):
    @sp.entrypoint()
    def default(self):
        pass


@sp.add_test(name="AcurastProxy")
def test():
    scenario = sp.test_scenario()

    BLOCK_LEVEL_1 = 1
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    job_creator = ImplicitInterface()

    scenario += job_creator

    scenario.show(
        sp.pack((1, "ASSIGN_JOB_PROCESSOR", sp.pack(sp.pair(1, alice.address))))
    )
    scenario.show(
        sp.keccak(
            sp.pack(sp.address("KT1B71rkEguZr9Zi2P29cV1hn6YdrkNDSCAk"))
            + sp.bytes("0x050001")
            + sp.bytes(
                "0x050707010000000c52454749535445525f4a4f4207070a0000001600008a8584be3718453e78923713a6966202b05f99c60a000000ee05070703030707050902000000250a00000020000000000000000000000000000000000000000000000000000000000000000007070707000007070509020000002907070a00000020111111111111111111111111111111111111111111111111111111111111111100000707030607070a00000001ff00010707000107070001070700010707020000000200000707070700b0d403070700b4f292aaf36107070098e4030707000000b4b8dba6f36107070a00000035697066733a2f2f516d64484c6942596174626e6150645573544d4d4746574534326353414a43485937426f374144583263644465610001"
            )
        )
    )

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
            validators=sp.set([alice.address]),
            minimum_endorsements=2,
        ),
        current_snapshot=2,
        snapshot_submissions=sp.map(),
        root=sp.big_map(
            {
                1: sp.bytes(
                    "0x00552aff0d1b8a20252c1f06786c93ac171ef13bb46bcd6677ddaccf1d1021c0"
                ),
                2: sp.bytes(
                    "0x9cd61921ec81965d9e3a4da48eca828c8d95415b9923b54e7d29a607fbfeac8d"
                ),
            }
        ),
    )
    scenario += validator

    acurastToken = AcurastTokenInterface()
    scenario += acurastToken

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
                            storage=sp.pack(
                                sp.record(
                                    job_id_seq=sp.nat(0),
                                    token_address=acurastToken.address,
                                )
                            ),
                        ),
                        OutgoingActionKind.FINALIZE_JOB: sp.record(
                            function=OutgoingActionLambda.finalize_job,
                            storage=sp.bytes("0x"),
                        ),
                    }
                ),
                ingoing_actions=sp.big_map(
                    {
                        IngoingActionKind.ASSIGN_JOB_PROCESSOR: sp.record(
                            function=IngoingActionLambda.assign_processor,
                            storage=sp.bytes("0x"),
                        ),
                        IngoingActionKind.FINALIZE_JOB: sp.record(
                            function=IngoingActionLambda.finalize_job,
                            storage=sp.pack(acurastToken.address),
                        ),
                    }
                ),
                paused=False,
            ),
            outgoing_seq_id=0,
            outgoing_registry=sp.big_map(),
            ingoing_seq_id=0,
            job_information=sp.big_map(),
        )
    )
    scenario += acurastProxy

    consumer = AcurastConsumer()
    consumer.update_initial_storage(
        sp.record(
            config=sp.record(
                acurast_proxy=acurastProxy.address,
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
            allowedSources=sp.some(sp.set([sp.bytes("0x" + "00" * 32)])),
            allowOnlyVerifiedSources=True,
            requiredModules=sp.set([0]),
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
                    reward=1000,
                    minReputation=sp.none,
                    instantMatch=sp.some(
                        sp.set(
                            [sp.record(source=sp.bytes("0x" + "11" * 32), startDelay=0)]
                        )
                    ),
                ),
                expectedFulfillmentFee=sp.mutez(1000),
            ),
        ),
        Type.RegisterJobAction,
    )
    register_job_bytes = scenario.compute(sp.pack(register_job_payload))
    register_job_action = sp.record(
        kind=OutgoingActionKind.REGISTER_JOB, payload=register_job_bytes
    )

    expected_fee = scenario.compute(
        sp.build_lambda(
            lambda arg: sp.set_type_expr(
                AcurastProxyInlined.compute_maximum_fees(
                    AcurastProxyInlined.compute_execution_count(
                        arg.startTime, arg.endTime, arg.interval
                    ),
                    arg.slots,
                    arg.expectedFulfillmentFee,
                ),
                sp.TMutez,
            )
        )(
            sp.record(
                startTime=register_job_payload.schedule.startTime,
                endTime=register_job_payload.schedule.endTime,
                interval=register_job_payload.schedule.interval,
                slots=register_job_payload.extra.requirements.slots,
                expectedFulfillmentFee=register_job_payload.extra.expectedFulfillmentFee,
            )
        )
    )
    actions = [register_job_action]
    acurastProxy.send_actions(actions).run(
        sender=job_creator.address, level=BLOCK_LEVEL_1, amount=expected_fee
    )
    # The contract balance should now be equal to the expected fee (only one job added yet)
    scenario.verify(acurastProxy.balance == expected_fee)

    # Get proof of inclusion
    proof = scenario.compute(
        aggregator.get_proof(sp.record(owner=acurastProxy.address, key=sp.pack(1)))
    )

    scenario.show(proof)

    acurastProxy.receive_actions(
        sp.record(
            snapshot=1,
            proof=[],
            leaves=[
                sp.record(
                    mmr_pos=0,
                    data=sp.bytes(
                        "0x05070700000707010000001441535349474e5f4a4f425f50524f434553534f520a0000002005070700010a000000160000eaeec9ada5305ad61fc452a5ee9f7d4f55f80467"
                    ),
                ),
                sp.record(
                    mmr_pos=1,
                    data=sp.bytes(
                        "0x05070700010707010000001441535349474e5f4a4f425f50524f434553534f520a0000002005070700010a000000160000edaa0fa299565241bd285414579f88705568c6b0"
                    ),
                ),
            ],
            mmr_size=3,
        )
    )

    acurastProxy.fulfill(sp.record(job_id=1, payload=sp.bytes("0x"))).run(
        sender=sp.address("tz1h4EsGunH2Ue1T2uNs8mfKZ8XZoQji3HcK")
    )

    # Allow job creators to withdraw remaining fee
    scenario.verify(job_creator.balance == sp.mutez(0))
    # acurastProxy.withdraw_remaining_fee(1).run(now=sp.timestamp(1678266546624))
    # scenario.verify(job_creator.balance == sp.mutez(11630))

    # Add 2 new jobs
    actions = [register_job_action,register_job_action]
    acurastProxy.send_actions(actions).run(
        sender=job_creator.address, level=BLOCK_LEVEL_1, amount=expected_fee
    )
    # Assign processors
    acurastProxy.receive_actions(
        sp.record(
            snapshot=2,
            proof=[
                sp.bytes(
                    "0x4f815ba60f512a92d199c973bcee1654860eddfe91c3fcc558275d3d4d58fea4"
                )
            ],
            leaves=[
                sp.record(
                    mmr_pos=0,
                    data=sp.bytes(
                        "0x05070700020707010000001441535349474e5f4a4f425f50524f434553534f520a0000002005070700020a000000160000eaeec9ada5305ad61fc452a5ee9f7d4f55f80467"
                    ),
                ),
                sp.record(
                    mmr_pos=1,
                    data=sp.bytes(
                        "0x05070700030707010000001441535349474e5f4a4f425f50524f434553534f520a0000002005070700030a000000160000eaeec9ada5305ad61fc452a5ee9f7d4f55f80467"
                    ),
                ),
            ],
            mmr_size=7,
        )
    )
