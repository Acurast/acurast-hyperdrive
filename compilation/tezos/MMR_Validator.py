import smartpy as sp

from contracts.tezos.MMR_Validator import MMR_Validator, MMR_Validator_Proxy

sp.add_compilation_target(
    "MMR_Validator",
    MMR_Validator(),
    storage=sp.record(
        config=sp.record(
            # Multi-sig address allowed to manage the contract
            governance_address=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            # Validators
            validators=sp.set(),
            # Minimum expected endorsements for a given state root to be considered valid
            minimum_endorsements=1,
        ),
        current_snapshot=1,
        snapshot_submissions=sp.map(),
        root=sp.big_map(),
    ),
)

sp.add_compilation_target(
    "MMR_Validator_Proxy",
    MMR_Validator_Proxy(),
    storage=sp.record(
        governance_address=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
        validator_address=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
    ),
)
