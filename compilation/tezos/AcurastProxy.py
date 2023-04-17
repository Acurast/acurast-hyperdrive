import smartpy as sp

from contracts.tezos.AcurastProxy import AcurastProxy, OutgoingActionLambda, OutgoingActionKind, IngoingActionLambda, IngoingActionKind, Type

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
        ingoing_seq_id=0,
        job_destination = sp.big_map()
    ),
)

sp.add_expression_compilation_target(
    "REGISTER_JOB_LAMBDA", sp.set_type_expr(
        [
            sp.variant("update_outgoing_actions",
                [
                    sp.variant(
                        "add",
                        sp.record(
                            kind=OutgoingActionKind.REGISTER_JOB,
                            function=sp.record(
                                function=OutgoingActionLambda.register_job,
                                storage=sp.record(
                                    version=1, data=sp.pack(sp.record(job_id_seq=0))
                                )
                            )
                        ),
                    )
                ]
            )
        ],
        Type.ConfigureArgument
    )
)
