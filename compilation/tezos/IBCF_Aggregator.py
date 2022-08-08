import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator

sp.add_compilation_target(
    "IBCF_Aggregator",
    IBCF_Aggregator(),
    storage=sp.record(
        config=sp.record(
            administrator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            signers=sp.set(),
            history_ttl=5,
            max_state_size=32,
            max_states=1000,
        ),
        merkle_history=sp.big_map(),
        merkle_history_indexes=[],
        latest_state_update=sp.big_map(),
    ),
)
