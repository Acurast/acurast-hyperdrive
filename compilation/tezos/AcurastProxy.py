import smartpy as sp

from contracts.tezos.AcurastProxy import (
    AcurastProxy,
    OutgoingActionLambda,
    OutgoingActionKind,
    IncomingActionLambda,
    IncomingActionKind,
    Type,
)

sp.add_compilation_target(
    "AcurastProxy",
    AcurastProxy(),
    storage=sp.record(
        store=sp.record(
            config=sp.record(
                governance_address=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
                merkle_aggregator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
                proof_validator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
                paused=False,
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
                            token_address=sp.address(
                                "KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"
                            ),
                        )
                    ),
                ),
                OutgoingActionKind.FINALIZE_JOB: sp.record(
                    function=OutgoingActionLambda.finalize_job,
                    storage=sp.bytes("0x"),
                ),
                # OutgoingActionKind.TELEPORT_ACRST: sp.record(
                #     function=OutgoingActionLambda.teleport_acrst,
                #     storage=sp.pack(sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT")),
                # ),
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
                    storage=sp.pack(sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT")),
                ),
            }
        ),
    ),
)

sp.add_expression_compilation_target(
    OutgoingActionKind.REGISTER_JOB,
    sp.set_type_expr(
        OutgoingActionLambda.register_job,
        sp.TLambda(
            Type.OutgoingActionLambdaArg,
            Type.OutgoingActionLambdaReturn,
            with_operations=True,
        ),
    ),
)

sp.add_expression_compilation_target(
    "OUT_" + OutgoingActionKind.NOOP,
    sp.set_type_expr(
        OutgoingActionLambda.noop,
        sp.TLambda(
            Type.OutgoingActionLambdaArg,
            Type.OutgoingActionLambdaReturn,
            with_operations=True,
        ),
    ),
)

sp.add_expression_compilation_target(
    "REGISTER_JOB_STORAGE",
    sp.pack(
        sp.record(
            job_id_seq=sp.nat(0),
            token_address=sp.address("KT1Vk5VhzwXez6zPFd46r9f9ZhYQkefRGbQr"),
            fa2_uusd = sp.record(
                address=sp.address("KT1XRPEPXbZK25r3Htzp2o1x7xdMMmfocKNW"),
                id=0
            )
        )
    ),
)
sp.add_expression_compilation_target(
    "FINALIZE_JOB_STORAGE", sp.pack(sp.record(
        address=sp.address("KT1XRPEPXbZK25r3Htzp2o1x7xdMMmfocKNW"),
        id=0
    ))
)

sp.add_expression_compilation_target(
    "OUT_" + OutgoingActionKind.FINALIZE_JOB,
    sp.set_type_expr(
        OutgoingActionLambda.finalize_job,
        sp.TLambda(
            Type.OutgoingActionLambdaArg,
            Type.OutgoingActionLambdaReturn,
            with_operations=True,
        ),
    ),
)
sp.add_expression_compilation_target(
    OutgoingActionKind.DEREGISTER_JOB,
    sp.set_type_expr(
        OutgoingActionLambda.deregister_job,
        sp.TLambda(
            Type.OutgoingActionLambdaArg,
            Type.OutgoingActionLambdaReturn,
            with_operations=True,
        ),
    ),
)
# sp.add_expression_compilation_target(
#     OutgoingActionKind.TELEPORT_ACRST,
#     sp.set_type_expr(
#         OutgoingActionLambda.teleport_acrst,
#         sp.TLambda(
#             Type.OutgoingActionLambdaArg,
#             Type.OutgoingActionLambdaReturn,
#             with_operations=True,
#         ),
#     ),
# )
# sp.add_expression_compilation_target(
#     "TELEPORT_ACRST_STORAGE",
#     sp.pack(sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT")),
# )

sp.add_expression_compilation_target(
    IncomingActionKind.ASSIGN_JOB_PROCESSOR,
    sp.set_type_expr(
        IncomingActionLambda.assign_processor,
        sp.TLambda(
            Type.IncomingActionLambdaArg,
            Type.IncomingActionLambdaReturn,
            with_operations=True,
        ),
    ),
)
sp.add_expression_compilation_target(
    IncomingActionKind.NOOP,
    sp.set_type_expr(
        IncomingActionLambda.noop,
        sp.TLambda(
            Type.IncomingActionLambdaArg,
            Type.IncomingActionLambdaReturn,
            with_operations=True,
        ),
    ),
)
sp.add_expression_compilation_target(
    IncomingActionKind.FINALIZE_JOB,
    sp.set_type_expr(
        IncomingActionLambda.finalize_job,
        sp.TLambda(
            Type.IncomingActionLambdaArg,
            Type.IncomingActionLambdaReturn,
            with_operations=True,
        ),
    ),
)

sp.add_expression_compilation_target(
    "CONFIGURE_OUT_NOOP",
    sp.set_type_expr(
        [
            sp.variant(
                "update_outgoing_actions",
                [
                    sp.variant(
                        "add",
                        sp.record(
                            kind=OutgoingActionKind.NOOP,
                            function=sp.record(
                                function=OutgoingActionLambda.noop,
                                storage=sp.bytes("0x"),
                            ),
                        ),
                    )
                ],
            )
        ],
        Type.ConfigureArgument,
    ),
)


sp.add_expression_compilation_target(
    "CONFIGURE",
    sp.set_type_expr(
        [
            sp.variant(
                "update_outgoing_actions",
                [
                    sp.variant(
                        "add",
                        sp.record(
                            kind=OutgoingActionKind.REGISTER_JOB,
                            function=sp.record(
                                function=OutgoingActionLambda.register_job,
                                storage=sp.pack(sp.nat(0)),
                            ),
                        ),
                    )
                ],
            )
        ],
        Type.ConfigureArgument,
    ),
)
