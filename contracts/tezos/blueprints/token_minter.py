# --------------------------------------------------------------------------
# This contract is used only for demonstration purpuses.
#
# The contract is a minimal client example for interacting if the IBCF
# protocol.
# ---------------------------------------------------------------------------
import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator_Type
from contracts.tezos.IBCF_Eth_Validator import Type as ValidatiorInterface
from contracts.tezos.utils.bytes import bytes_of_string

class Error:
    INVALID_CONTRACT = "INVALID_CONTRACT"

class Type:
    TeleportTable = sp.TBigMap( """ETH address""" sp.TBytes, """counter""" sp.TNat)
    TeleportArgument = sp.TRecord(eth_address = sp.TBytes, amount = sp.TNat)

class IBCF_RemoteMinter(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                registry = Type.TeleportTable,
                minter_address = sp.TAddress,
                merkle_aggregator = sp.TAddress,
                eth_nonce = sp.TNat,
            )
        )

    @sp.entry_point(parameter_type = Type.TeleportArgument)
    def teleport(self, param):
        # Update recipient counter
        counter = sp.compute(self.data.registry.get(param.eth_address, default_value = 0) + 1)
        self.data.registry[param.eth_address] = counter

        # Encode payload
        payload = sp.pair(param.eth_address, param.amount, counter)

        # Prepare message
        param = sp.record(key = param.eth_address, value = sp.bytes("0x00"))
        contract = sp.contract(IBCF_Aggregator_Type.Insert_argument, self.data.merkle_aggregator, "insert").open_some(Error.INVALID_CONTRACT)

        # Emit teleport
        sp.transfer(param, sp.mutez(0), contract)
