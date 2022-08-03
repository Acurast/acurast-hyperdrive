# --------------------------------------------------------------------------
# This contract is used only for demonstration purpuses.
#
# The contract is a minimal client example for interacting if the IBCF
# protocol.
# ---------------------------------------------------------------------------
import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type
from contracts.tezos.IBCF_Eth_Validator import Type as ValidatiorInterface


class Error:
    EXPECTING_PONG = "EXPECTING_PONG"
    EXPECTING_PING = "EXPECTING_PING"
    INVALID_COUNTER = "INVALID_COUNTER"
    INVALID_CONTRACT = "INVALID_CONTRACT"
    INVALID_VIEW = "INVALID_VIEW"


class Inlined:
    @staticmethod
    def string_of_nat(number):
        """Convert an int into a string"""
        c = sp.map({x: str(x) for x in range(0, 10)})
        x = sp.local("x", number)
        arr = sp.local("arr", [])

        with sp.if_(x.value == 0):
            arr.value.push("0")
        with sp.while_(0 < x.value):
            arr.value.push(c[x.value % 10])
            x.value //= 10

        result = sp.local("result", sp.concat(arr.value))

        return result.value

    @staticmethod
    def bytes_of_string(text):
        b = sp.pack(text)
        # Remove (packed prefix), (Data identifier) and (string length)
        # - Packed prefix: 0x05 (1 byte)
        # - Data identifier: (string = 0x01) (1 byte)
        # - String length (4 bytes)
        return sp.slice(b, 6, sp.as_nat(sp.len(b) - 6)).open_some(
            "Could not encode string to bytes."
        )

    @staticmethod
    def string_of_bytes(b):
        packedBytes = sp.concat(
            [
                sp.bytes("0x05"),
                sp.bytes("0x01"),
                sp.bytes("0x00000001"),
                sp.slice(b, 1, 1).open_some(),
            ]
        )
        return sp.unpack(packedBytes, sp.TString).open_some(sp.unit)


class IBCF_Client(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                eth_contract=sp.TBytes,
                storage_slot=sp.TBytes,
                ibcf_tezos_state=sp.TAddress,
                ibcf_eth_validator=sp.TAddress,
                counter=sp.TNat,
            )
        )

    @sp.entry_point()
    def update_storage(self, param):
        self.data = param

    @sp.entry_point()
    def ping(self):
        # Pings can only happen when counter is even
        sp.verify(self.data.counter % 2 == 0, Error.EXPECTING_PONG)

        # Increase counter
        self.data.counter += 1

        packed_counter = sp.compute(
            Inlined.bytes_of_string(Inlined.string_of_nat(self.data.counter))
        )

        # Send ping
        param = sp.record(key=Inlined.bytes_of_string("counter"), value=packed_counter)
        contract = sp.contract(
            Type.InsertArgument, self.data.ibcf_tezos_state, "insert"
        ).open_some(Error.INVALID_CONTRACT)
        sp.transfer(param, sp.mutez(0), contract)

    @sp.entry_point(
        parameter_type=sp.TRecord(
            block_number=sp.TNat,
            account_proof_rlp=sp.TBytes,
            storage_proof_rlp=sp.TBytes,
        )
    )
    def pong(self, param):
        # Pongs can only happen when counter is odd
        sp.verify(self.data.counter % 2 == 1, Error.EXPECTING_PING)

        # Increase counter
        self.data.counter += 1

        response = sp.view(
            "validate_proof",
            self.data.ibcf_eth_validator,
            sp.set_type_expr(
                sp.record(
                    block_number=param.block_number,
                    account=self.data.eth_contract,
                    account_proof_rlp=param.account_proof_rlp,
                    storage_slot=self.data.storage_slot,
                    storage_proof_rlp=param.storage_proof_rlp,
                ),
                ValidatiorInterface.Validate_storage_proof_argument,
            ),
            t=sp.TBytes,
        ).open_some(Error.INVALID_VIEW)

        sp.verify(
            Inlined.string_of_bytes(response)
            == Inlined.string_of_nat(self.data.counter),
            (Error.INVALID_COUNTER),
        )
