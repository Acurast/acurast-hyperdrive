import smartpy as sp

from contracts.tezos.blueprints.IBCF_Bridge import IBCF_Bridge

sp.add_compilation_target(
    "IBCF_Bridge",
    IBCF_Bridge(),
    storage=sp.record(
        nonce=0,
        wrap_nonce=sp.big_map(),
        registry=sp.big_map(),
        merkle_aggregator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
        proof_validator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
        asset_address=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
        eth_bridge_address=sp.bytes("0x00"),
    ),
)
