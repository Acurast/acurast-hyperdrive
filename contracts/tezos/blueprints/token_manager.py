# --------------------------------------------------------------------------
# This contract is used only for demonstration purpuses.
#
# The contract is a minimal client example for interacting if the IBCF
# protocol.
# ---------------------------------------------------------------------------
import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type
from contracts.tezos.IBCF_Eth_Validator import Type as ValidatiorInterface
from contracts.tezos.utils.bytes import bytes_of_string

class Error:
    EXPECTING_PONG = "EXPECTING_PONG"
    EXPECTING_PING = "EXPECTING_PING"
    INVALID_COUNTER = "INVALID_COUNTER"
    INVALID_CONTRACT = "INVALID_CONTRACT"
    INVALID_VIEW = "INVALID_VIEW"

class IBCF_TokenManager(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                eth_contract=sp.TBytes,
                storage_slot=sp.TBytes,
                tezos_state_aggregator=sp.TAddress,
                eth_state_validator=sp.TAddress,
                eth_nonce=sp.TNat,
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
            bytes_of_string(Inlined.string_of_nat(self.data.counter))
        )

        # Send ping
        param = sp.record(key=bytes_of_string("counter"), value=packed_counter)
        contract = sp.contract(
            Type.Insert_argument, self.data.ibcf_tezos_state, "insert"
        ).open_some(Error.INVALID_CONTRACT)
        sp.transfer(param, sp.mutez(0), contract)

    @sp.entry_point(
        parameter_type=sp.TRecord(
            block_number=sp.TNat,
            account_proof_rlp=sp.TBytes,
            storage_proof_rlp=sp.TBytes,
        )
    )
    def confirm_pong(self, param):
        # Pongs can only happen when counter is odd
        sp.verify(self.data.counter % 2 == 1, Error.EXPECTING_PING)

        # Increase counter
        self.data.counter += 1

        response = sp.view(
            "validate_storage_proof",
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
