import smartpy as sp

from contracts.tezos.utils.bytes import Bytes

class String:
    @staticmethod
    def of_bytes(b):
        bytes_of_nat = sp.build_lambda(Bytes.of_nat)
        # Encode the string length
        # Each utf-8 char is represented by 2 nibble (1 byte)
        lengthBytes = sp.local("lengthBytes", bytes_of_nat(sp.len(b)))
        with sp.while_(sp.len(lengthBytes.value) < 4):
            lengthBytes.value = sp.bytes("0x00") + lengthBytes.value
        # Append (packed prefix) + (Data identifier) + (string length) + (string bytes)
        # - Packed prefix: 0x05 (1 byte)
        # - Data identifier: (string = 0x01) (1 byte)
        # - String length (4 bytes)
        # - String bytes
        packedBytes = sp.concat([sp.bytes("0x05"), sp.bytes("0x01"), lengthBytes.value, b])
        return sp.unpack(packedBytes, sp.TString).open_some("Could not decode bytes to string")
