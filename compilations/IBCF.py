import smartpy as sp

from contracts.merkle_patricia_tree import IBCF, EMPTY_TREE
from contracts.utils.bytes import bytes_to_bits

sp.add_compilation_target(
    "merkle_patricia_tree",
    IBCF(),
    storage=sp.record(
        bytes_to_bits=bytes_to_bits,
        administrators=sp.set(),
        merkle_history=sp.big_map(),
        tree=EMPTY_TREE,
    ),
)
