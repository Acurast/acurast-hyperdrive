# --------------------------------------------------------------------------
# This contract implements a bridging protocol.
#
# It allows users to wrap/unwrap Ethereum assets on the Tezos blockchain.
# --------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type as IBCF_Aggregator_Type
from contracts.tezos.IBCF_Eth_Validator import Type as ValidatorInterface
from contracts.tezos.libs.fa2_lib import (
    Fa2SingleAsset,
    BurnSingleAsset,
    MintSingleAsset,
    Admin,
)
from contracts.tezos.libs.utils import RLP, Bytes


class Constant:
    ETH_DESTINATION_INDEX = sp.bytes(
        "0x0000000000000000000000000000000000000000000000000000000000000005"
    )
    ETH_AMOUNT_INDEX = sp.bytes(
        "0x0000000000000000000000000000000000000000000000000000000000000006"
    )


class Error:
    INVALID_CONTRACT = "INVALID_CONTRACT"
    INVALID_VIEW = "INVALID_VIEW"
    INVALID_DESTINATION = "INVALID_DESTINATION"
    ALREADY_PROCESSED = "ALREADY_PROCESSED"


class Type:
    Unwrap = sp.TRecord(
        level=sp.TNat, destination=sp.TBytes, amount=sp.TNat
    ).right_comb()
    UnwrapArgument = sp.TRecord(destination=sp.TBytes, amount=sp.TNat).right_comb()
    UnwrapTable = sp.TBigMap(sp.TNat, Unwrap)  # (nonce => Unwrap)
    WrapArgument = sp.TRecord(
        block_number=sp.TNat,
        nonce=sp.TBytes,
        account_proof_rlp=sp.TBytes,
        destination_proof_rlp=sp.TBytes,
        amount_proof_rlp=sp.TBytes,
    ).right_comb()


class Inlined:
    @staticmethod
    def getBurnEntrypoint(asset_address):
        return sp.contract(
            sp.TList(
                sp.TRecord(
                    from_=sp.TAddress,
                    token_id=sp.TNat,
                    amount=sp.TNat,
                ).layout(("from_", ("token_id", "amount")))
            ),
            asset_address,
            "burn",
        ).open_some(Error.INVALID_CONTRACT)

    @staticmethod
    def getMintEntrypoint(asset_address):
        return sp.contract(
            sp.TList(
                sp.TRecord(to_=sp.TAddress, amount=sp.TNat).layout(("to_", "amount"))
            ),
            asset_address,
            "mint",
        ).open_some(Error.INVALID_CONTRACT)

    @staticmethod
    def computeStorageSlots(nonce):
        destination_slot = sp.keccak(nonce + Constant.ETH_DESTINATION_INDEX)
        amount_slot = sp.keccak(nonce + Constant.ETH_AMOUNT_INDEX)
        return (destination_slot, amount_slot)


class IBCF_Bridge(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                nonce=sp.TNat,
                wrap_nonce=sp.TBigMap(sp.TBytes, sp.TUnit),
                registry=Type.UnwrapTable,
                merkle_aggregator=sp.TAddress,
                proof_validator=sp.TAddress,
                asset_address=sp.TAddress,
                eth_bridge_address=sp.TBytes,
            )
        )

    @sp.entry_point(parameter_type=Type.UnwrapArgument)
    def unwrap(self, param):
        burn_method = Inlined.getBurnEntrypoint(self.data.asset_address)

        # Register unwrap
        self.data.nonce += 1
        nonce = sp.compute(self.data.nonce)
        self.data.registry[nonce] = sp.record(
            level=sp.level,
            destination=param.destination,
            amount=param.amount,
        )

        encode_nat_lambda = sp.compute(RLP.Lambda.encode_nat())
        with_length_prefix_lambda = sp.compute(RLP.Lambda.with_length_prefix())
        encode_list_lambda = sp.compute(RLP.Lambda.encode_list())

        # Encode payload
        rlp_destination = with_length_prefix_lambda(param.destination)
        rlp_amount = encode_nat_lambda(param.amount)
        rlp_nonce = encode_nat_lambda(nonce)
        payload = encode_list_lambda([rlp_destination, rlp_amount])

        # Prepare message
        contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, self.data.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_CONTRACT)

        # Emit unwrap operation
        state_param = sp.record(key=rlp_nonce, value=payload)
        sp.transfer(state_param, sp.mutez(0), contract)

        # Burn tokens
        burn_param = sp.record(
            from_=sp.sender,
            token_id=0,
            amount=param.amount,
        )
        sp.transfer([burn_param], sp.mutez(0), burn_method)

    @sp.entry_point(parameter_type=Type.WrapArgument)
    def wrap(self, param):
        mint_method = Inlined.getMintEntrypoint(self.data.asset_address)

        decode_nat_lambda = sp.compute(RLP.Lambda.decode_nat())
        without_length_prefix = sp.compute(RLP.Lambda.without_length_prefix())

        # Verify that wrap was not yet processed, fail otherwise
        nonce = param.nonce
        sp.verify(~self.data.wrap_nonce.contains(nonce), Error.ALREADY_PROCESSED)
        # Set nonce as processed
        self.data.wrap_nonce[nonce] = sp.unit

        # Compute the storage slot for the ethereum proof
        (destination_slot, amount_slot) = Inlined.computeStorageSlots(nonce)

        # Validate proof and extract storage value (The amount to be wrapped and the destination address)
        rlp_destination = sp.view(
            "validate_storage_proof",
            self.data.proof_validator,
            sp.set_type_expr(
                sp.record(
                    block_number=param.block_number,
                    account=self.data.eth_bridge_address,
                    account_proof_rlp=param.account_proof_rlp,
                    storage_slot=destination_slot,
                    storage_proof_rlp=param.destination_proof_rlp,
                ),
                ValidatorInterface.Validate_storage_proof_argument,
            ),
            t=sp.TBytes,
        ).open_some(Error.INVALID_VIEW)
        rlp_amount = sp.view(
            "validate_storage_proof",
            self.data.proof_validator,
            sp.set_type_expr(
                sp.record(
                    block_number=param.block_number,
                    account=self.data.eth_bridge_address,
                    account_proof_rlp=param.account_proof_rlp,
                    storage_slot=amount_slot,
                    storage_proof_rlp=param.amount_proof_rlp,
                ),
                ValidatorInterface.Validate_storage_proof_argument,
            ),
            t=sp.TBytes,
        ).open_some(Error.INVALID_VIEW)

        # Decode destination and amount
        destination = sp.unpack(
            sp.slice(rlp_destination, 1, 28).open_some(Error.INVALID_DESTINATION),
            sp.TAddress,
        ).open_some(Error.INVALID_DESTINATION)
        amount = decode_nat_lambda(sp.compute(rlp_amount))

        # Mint tokens
        sp.transfer(
            [sp.record(to_=destination, amount=amount)], sp.mutez(0), mint_method
        )
