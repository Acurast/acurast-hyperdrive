import smartpy as sp

from contracts.tezos.utils.math import Math


class Nat:
    @staticmethod
    def of_bytes(b):
        length = sp.compute(sp.len(b))
        decimal = sp.local("decimal", sp.nat(0))
        with sp.for_("_pos", sp.range(0, length)) as pos:
            byte = sp.compute(sp.slice(b, pos, 1).open_some())
            base = sp.compute(sp.as_nat(length - (pos + 1)) * 2)
            # - Packed prefix: 0x05 (1 byte)
            # - Data identifier: (bytes = 0x0a) (1 byte)
            # - Length ("0x00000020" = 32) (4 bytes)
            # - Data (32 bytes)
            packedBytes = sp.bytes("0x050a00000020") + byte + sp.bytes("0x" + "00" * 31)
            decimal.value += sp.as_nat(
                sp.to_int(sp.unpack(packedBytes, sp.TBls12_381_fr).open_some())
            ) * Math.pow(16, base)

        sp.result(decimal.value)
