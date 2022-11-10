import smartpy as sp

from contracts.tezos.blueprints.IBCF_AssetTeleport import IBCF_AssetTeleport

sp.add_compilation_target(
    "IBCF_AssetTeleport",
    IBCF_AssetTeleport(),
    storage=sp.record(
        registry=sp.big_map(),
        minter_address=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
        merkle_aggregator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
    ),
)
