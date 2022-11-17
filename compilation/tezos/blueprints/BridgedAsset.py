import smartpy as sp
from contracts.tezos.blueprints.Asset import Asset

sp.add_compilation_target(
    "BridgedAsset",
    Asset(
        metadata        = sp.big_map(),
        administrator   = sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT")
    )
)
