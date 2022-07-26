import smartpy as sp

from contracts.tezos.state_aggregator import IBCF
from contracts.tezos.utils.bytes import bytes_to_bits

sp.add_compilation_target(
    "state_aggregator",
    IBCF(),
    storage=sp.record(
        config=sp.record(
            administrator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            signers=sp.set(),
            history_ttl=5,
            max_state_size=32,
            max_states=1000,
        ),
        bytes_to_bits=bytes_to_bits,
        merkle_history=sp.big_map(),
        merkle_history_indexes=[],
    ),
)
