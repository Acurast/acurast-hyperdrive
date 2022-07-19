import smartpy as sp

from contracts.tezos.state_aggregator import IBCF, EMPTY_TREE
from contracts.tezos.utils.bytes import bytes_to_bits

sp.add_compilation_target(
    "state_aggregator",
    IBCF(),
    storage=sp.record(
        bytes_to_bits=bytes_to_bits,
        administrators=sp.set(),
        merkle_history=sp.big_map(),
    ),
)
