# --------------------------------------------------------------------------
# This contract is a token teleporter used to provide provable orders
# for minting the assets on ethereum.
# --------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type as IBCF_Aggregator_Type
from contracts.tezos.IBCF_Eth_Validator import Type as ValidatiorInterface
import contracts.tezos.utils.rlp as RLP


class Error:
    INVALID_CONTRACT = "INVALID_CONTRACT"
    NOT_MINTER = "NOT_MINTER"


class Type:
    TeleportTable = sp.TBigMap(sp.TBytes, sp.TNat)  # (ETH address, counter)
    TeleportArgument = sp.TRecord(eth_address=sp.TBytes, amount=sp.TNat)


class RLP_encoder:
    @staticmethod
    def encode_list():
        return sp.compute(sp.build_lambda(RLP.Encoder.encode_list))

    @staticmethod
    def encode_nat():
        return sp.compute(sp.build_lambda(RLP.Encoder.encode_nat))

    @staticmethod
    def with_length_prefix():
        return sp.compute(sp.build_lambda(RLP.Encoder.with_length_prefix))


class Inlined:
    @staticmethod
    def failIfNotMinter(self):
        """
        This method when used, ensures that only the minter is allowed to call a given entrypoint
        """
        sp.verify(self.data.minter_address == sp.sender, Error.NOT_MINTER)


class IBCF_AssetTeleport(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                registry=Type.TeleportTable,
                minter_address=sp.TAddress,
                merkle_aggregator=sp.TAddress,
            )
        )

    @sp.entry_point(parameter_type=Type.TeleportArgument)
    def teleport(self, param):
        Inlined.failIfNotMinter(self)

        # Update recipient counter
        counter = sp.compute(
            self.data.registry.get(param.eth_address, default_value=0) + 1
        )
        self.data.registry[param.eth_address] = counter

        encode_nat_lambda = RLP_encoder.encode_nat()
        with_length_prefix_lambda = RLP_encoder.with_length_prefix()
        encode_list_lambda = RLP_encoder.encode_list()

        # Encode payload
        rlp_eth_address = with_length_prefix_lambda(param.eth_address)
        rlp_amount = encode_nat_lambda(param.amount)
        rlp_counter = encode_nat_lambda(counter)
        payload = encode_list_lambda([rlp_eth_address, rlp_amount, rlp_counter])

        # Prepare message
        param = sp.record(key=param.eth_address + rlp_counter, value=payload)
        contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, self.data.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_CONTRACT)

        # Emit teleport
        sp.transfer(param, sp.mutez(0), contract)
