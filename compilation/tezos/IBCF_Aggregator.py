import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, EMPTY_TREE

sp.add_compilation_target(
    "IBCF_Aggregator",
    IBCF_Aggregator(),
    storage=sp.record(
        config=sp.record(
            administrator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            max_state_size=32,
            snapshot_duration=5
        ),
        snapshot_start_level = 0,
        snapshot_counter            = 0,
        snapshot_level              = sp.big_map(),
        merkle_tree                 = EMPTY_TREE
    ),
)
