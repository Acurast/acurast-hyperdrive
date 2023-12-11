import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, EMPTY_TREE
from contracts.tezos.AcurastProxy import (
    AcurastProxy,
    OutgoingActionLambda,
    IncomingActionLambda,
    OutgoingActionKind,
    IncomingActionKind,
    Type,
    Inlined as AcurastProxyInlined,
    Acurast_Token_Interface,
)
from contracts.tezos.libs.utils import Decorator
from contracts.tezos.AcurastConsumer import AcurastConsumer
from contracts.tezos.MMR_Validator import MMR_Validator
import contracts.tezos.libs.fa2_lib as fa2

class AcurastTokenInterface(sp.Contract):
    @sp.entrypoint()
    def burn_tokens(self, arg):
        sp.set_type(arg, Acurast_Token_Interface.BurnMintTokens)
        pass

    @sp.entrypoint()
    def mint_tokens(self, arg):
        sp.set_type(arg, Acurast_Token_Interface.BurnMintTokens)
        pass

    @sp.onchain_view()
    def get_balance(self, arg):
        sp.set_type(arg, sp.TRecord(owner=sp.TAddress, token_id=sp.TNat))
        sp.result(sp.nat(10000))

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

    tok0_md = fa2.make_metadata(name="Token Zero", decimals=1, symbol="Tok0")
    TOKEN_METADATA = [tok0_md]
    METADATA = sp.utils.metadata_of_url("ipfs://example")
    ledger = {
        (job_creator.address, 0): 1000000000000,
    }
    token_metadata = TOKEN_METADATA
    uusdToken = fa2.Fa2Fungible(
        metadata=METADATA,
        ledger=ledger,
        token_metadata=token_metadata,
    )
    scenario += uusdToken

    acurastProxy = AcurastProxy()
    acurastProxy.update_initial_storage(
        sp.record(
            store=sp.record(
                config=sp.record(
                    governance_address=admin.address,
                    merkle_aggregator=aggregator.address,
                    proof_validator=validator.address,
                    paused=True,
                ),
                outgoing_seq_id=0,
                outgoing_registry=sp.big_map(),
                incoming_seq_id=0,
                job_information=sp.big_map(),
            ),
            outgoing_actions=sp.big_map(
                {
                    OutgoingActionKind.REGISTER_JOB: sp.record(
                        function=OutgoingActionLambda.register_job,
                        storage=sp.pack(
                            sp.record(
                                job_id_seq=sp.nat(0),
                                token_address=acurastToken.address,
                                fa2_uusd = sp.record(
                                    address=uusdToken.address,
                                    id=0
                                )
                            )
                        ),
                    ),
                    OutgoingActionKind.FINALIZE_JOB: sp.record(
                        function=OutgoingActionLambda.finalize_job,
                        storage=sp.bytes("0x"),
                    ),
                    OutgoingActionKind.SET_JOB_ENVIRONMENT: sp.record(
                        function=OutgoingActionLambda.set_job_environment,
                        storage=sp.bytes("0x"),
                    ),
                }
            ),
            incoming_actions=sp.big_map(
                {
                    IncomingActionKind.ASSIGN_JOB_PROCESSOR: sp.record(
                        function=IncomingActionLambda.assign_processor,
                        storage=sp.bytes("0x"),
                    ),
                    IncomingActionKind.FINALIZE_JOB: sp.record(
                        function=IncomingActionLambda.finalize_job,
                        storage=sp.pack(acurastToken.address),
                    ),
                }
            ),
        ),
    )
    scenario += acurastProxy

    add_noop_outgoing_action = sp.variant(
        "add",
        sp.record(
            kind=OutgoingActionKind.NOOP,
            function=sp.record(
                function = sp.set_type_expr(
                    OutgoingActionLambda.noop,
                    sp.TLambda(
                        Type.OutgoingActionLambdaArg,
                        Type.OutgoingActionLambdaReturn,
                        with_operations=True,
                    ),
                ),
                storage = sp.bytes("0x")
            )
        )
    )
    acurastProxy.configure([sp.variant("update_outgoing_actions", [add_noop_outgoing_action])]).run(
        sender=admin.address
    )

    consumer = AcurastConsumer()
    consumer.update_initial_storage(
        sp.record(
            config=sp.record(
                acurast_proxy=acurastProxy.address,
            )
        )
    )
    scenario += consumer

    ## Test generic call in configure entrypoint

    scenario.verify(acurastProxy.balance == sp.tez(0))
    scenario.verify(acurastProxy.data.store.config.paused)

    @Decorator.generate_lambda(with_storage="read-write", with_operations=True)
    def generic_action(self, unit):
        sp.send(sp.sender, sp.tez(1))

        self.data.store.config.paused = False

    acurastProxy.configure([sp.variant("generic", generic_action)]).run(
        sender=admin.address, amount=sp.tez(1)
    )

    scenario.verify(acurastProxy.balance == sp.tez(0))
    scenario.verify(~acurastProxy.data.store.config.paused)

    ##! Test generic call in configure entrypoint

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
                startTime=1697618400000,
                endTime=1697618700000,
                interval=60000,
                maxStartDelay=0,
            ),
            memory=1,
            networkRequests=1,
            storage=1,
            extra=sp.record(
                requirements=sp.record(
                    slots=2,
                    reward=10000000000,
                    minReputation=sp.none,
                    instantMatch=sp.some(
                        sp.set(
                            [sp.record(source=sp.bytes("0x" + "11" * 32), startDelay=0)]
                        )
                    ),
                ),
                expectedFulfillmentFee=sp.mutez(2000),
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
    # Set proxy as operator
    uusdToken.update_operators([sp.variant("add_operator", sp.record(owner=job_creator.address, operator=acurastProxy.address, token_id=0))]).run(sender=job_creator.address)

    # Register job
    actions = [register_job_action]
    acurastProxy.send_actions(actions).run(
        sender=job_creator.address, level=BLOCK_LEVEL_1, amount=expected_fee
    )

    # Unset proxy as operator
    uusdToken.update_operators([sp.variant("remove_operator", sp.record(owner=job_creator.address, operator=acurastProxy.address, token_id=0))]).run(sender=job_creator.address)

    scenario.verify(uusdToken.data.ledger[(acurastProxy.address, 0)] == 6500000000)
    scenario.verify(uusdToken.data.ledger[(job_creator.address, 0)] == 993500000000)

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

    for x in range(5):
        acurastProxy.fulfill(sp.record(job_id=1, payload=sp.bytes("0x"))).run(
            sender=sp.address("tz1h4EsGunH2Ue1T2uNs8mfKZ8XZoQji3HcK")
        )
        acurastProxy.fulfill(sp.record(job_id=1, payload=sp.bytes("0x"))).run(
            sender=sp.address("tz1hJgZdhnRGvg5XD6pYxRCsbWh4jg5HQ476")
        )

    scenario.show(acurastProxy.data.store.job_information[1].remaining_fee == sp.mutez(0))

    # Allow job creators to withdraw remaining fee
    scenario.verify(job_creator.balance == sp.mutez(0))

    # Set proxy as operator
    uusdToken.update_operators([sp.variant("add_operator", sp.record(owner=job_creator.address, operator=acurastProxy.address, token_id=0))]).run(sender=job_creator.address)

    # Add 2 new jobs
    actions = [register_job_action, register_job_action]
    acurastProxy.send_actions(actions).run(
        sender=job_creator.address, level=BLOCK_LEVEL_1, amount=expected_fee
    )

    # Unset proxy as operator
    uusdToken.update_operators([sp.variant("remove_operator", sp.record(owner=job_creator.address, operator=acurastProxy.address, token_id=0))]).run(sender=job_creator.address)

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

    # Set job environment
    set_job_environment_payload = sp.set_type_expr(
        sp.record(
            job_id = sp.nat(1),
            public_key = sp.bytes("0x028160f8d4230005bb3b6aa08078fe73b33b8db12d1d7b2083d593e585e64b061a"),
            processors = sp.map({
                sp.bytes("0xd80a8b0d800a3320528693947f7317871b2d51e5f3c8f3d0d4e4f7e6938ed68f"): sp.map({
                    sp.bytes("0xabcd"): sp.bytes("0xabcd")
                })
            })
        ),
        Type.SetJobEnvironmentAction
    )
    set_job_environment_bytes = scenario.compute(sp.pack(set_job_environment_payload))
    scenario.show(set_job_environment_bytes)
    set_job_environment_action = sp.record(
        kind=OutgoingActionKind.SET_JOB_ENVIRONMENT, payload=set_job_environment_bytes
    )
    actions = [set_job_environment_action]
    acurastProxy.send_actions(actions).run(
        sender=job_creator.address, level=BLOCK_LEVEL_1, amount=expected_fee
    )
