import smartpy as sp

from contracts.tezos.blueprints.IBCF_Crowdfunding import IBCF_Crowdfunding

sp.add_compilation_target(
    "IBCF_Crowdfunding",
    IBCF_Crowdfunding(),
    storage=sp.record(
        ibcf=sp.record(
            nonce=sp.big_map(),
            proof_validator=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            evm_address=sp.bytes("0x00"),
        ),
        recipient=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
        tezos_funding=sp.map(),
        eth_funding=sp.map(),
    ),
)
