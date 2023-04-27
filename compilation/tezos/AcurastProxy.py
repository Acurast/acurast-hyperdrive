import smartpy as sp

from contracts.tezos.AcurastProxy import (
    AcurastProxy,
    OutgoingActionLambda,
    OutgoingActionKind,
    IngoingActionLambda,
    IngoingActionKind,
    Type,
)

sp.add_compilation_target(
    "AcurastProxy",
    AcurastProxy(),
    storage=sp.record(
        config=sp.record(
            governance_address=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            merkle_aggregator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            proof_validator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
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
                        storage=sp.record(version=1, data=sp.bytes("0x")),
                    ),
                }
            ),
        ),
        outgoing_seq_id=0,
        outgoing_registry=sp.big_map(),
        ingoing_seq_id=0,
        job_information=sp.big_map(),
    ),
)

sp.add_expression_compilation_target(
    "REGISTER_JOB",
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
    "REGISTER_JOB_STORAGE", sp.pack(sp.record(job_id_seq=0))
)

sp.add_expression_compilation_target(
    "ASSIGN_PROCESSOR",
    sp.set_type_expr(
        IngoingActionLambda.assign_processor,
        sp.TLambda(
            Type.IngoingActionLambdaArg,
            Type.IngoingActionLambdaReturn,
            with_operations=True,
        ),
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
                                storage=sp.record(
                                    version=1, data=sp.pack(sp.record(job_id_seq=0))
                                ),
                            ),
                        ),
                    )
                ],
            )
        ],
        Type.ConfigureArgument,
    ),
)
