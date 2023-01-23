import smartpy as sp

from contracts.tezos.libs.fa2_lib import (
    Fa2SingleAsset,
    BurnSingleAsset,
    MintSingleAsset,
    Admin,
)


class Asset(Fa2SingleAsset, BurnSingleAsset, MintSingleAsset, Admin):
    def __init__(self, metadata, administrator):
        Fa2SingleAsset.__init__(
            self, metadata, token_metadata=sp.map({"": sp.bytes("0x")})
        )
        Admin.__init__(self, administrator)
