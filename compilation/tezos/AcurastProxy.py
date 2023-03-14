import smartpy as sp

from contracts.tezos.AcurastProxy import AcurastProxy, ActionLambda

sp.add_compilation_target(
    "AcurastProxy",
    AcurastProxy(),
    storage=sp.record(
        config=sp.record(
            governance_address=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            merkle_aggregator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            proof_validator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            authorized_actions=sp.big_map(
                {
                    "REGISTER_JOB": sp.record(
                        function=ActionLambda.register_job,
                        storage=sp.record(
                            version=0, data=sp.pack(sp.record(job_id_seq=0))
                        ),
                    ),
                }
            ),
        ),
        outgoing_counter=0,
        registry=sp.big_map(),
    ),
)
