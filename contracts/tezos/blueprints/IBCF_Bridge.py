# --------------------------------------------------------------------------
# This contract implements a bridging protocol.
#
# It allows users to wrap/unwrap Ethereum assets on the Tezos blockchain.
# --------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type as IBCF_Aggregator_Type
from contracts.tezos.IBCF_Eth_Validator import Type as ValidatiorInterface
from contracts.tezos.utils.fa2_lib import Fa2SingleAsset, BurnSingleAsset, MintSingleAsset, Admin
from contracts.tezos.utils.bytes import Bytes
import contracts.tezos.utils.rlp as RLP

class Constant:
    ETH_SLOT_INDEX = sp.bytes("0x0000000000000000000000000000000000000000000000000000000000000005")

class Error:
    INVALID_CONTRACT = "INVALID_CONTRACT"
    INVALID_VIEW = "INVALID_VIEW"

class Type:
    UnwrapTable     = sp.TBigMap(sp.TBytes, sp.TNat)  # (ETH address, counter)
    UnwrapArgument  = sp.TRecord(eth_address=sp.TBytes, amount=sp.TNat)
    WrapArgument    = sp.TRecord(
                        block_number        = sp.TNat,
                        account_proof_rlp   = sp.TBytes,
                        storage_proof_rlp   = sp.TBytes,
                        destination         = sp.TAddress
                    )

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
            ), asset_address, "burn"
        ).open_some(Error.INVALID_CONTRACT)

    @staticmethod
    def getMintEntrypoint(asset_address):
        return sp.contract(
            sp.TList(
                sp.TRecord(to_=sp.TAddress, amount=sp.TNat).layout(("to_", "amount"))
            ), asset_address, "mint"
        ).open_some(Error.INVALID_CONTRACT)

    @staticmethod
    def computeStorageSlot(destination, nonce):
        pad_start_lambda = sp.build_lambda(Bytes.pad_start)
        bytes_of_nat = sp.build_lambda(Bytes.of_nat)
        nonce_encoded = pad_start_lambda((bytes_of_nat(nonce), sp.bytes("0x00"), 32))
        return sp.keccak(sp.pack(destination) + nonce_encoded + Constant.ETH_SLOT_INDEX)

class IBCF_Bridge(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                registry            = Type.UnwrapTable,
                ethereum_nonce      = sp.TBigMap(sp.TAddress, sp.TNat),
                merkle_aggregator   = sp.TAddress,
                proof_validator     = sp.TAddress,
                asset_address       = sp.TAddress,
                eth_bridge_address  = sp.TBytes,
            )
        )

    @sp.entry_point(parameter_type=Type.UnwrapArgument)
    def unwrap(self, param):
        burn_method = Inlined.getBurnEntrypoint(self.data.asset_address)

        # Update recipient counter
        counter = sp.compute(
            self.data.registry.get(param.eth_address, default_value = 0) + 1
        )
        self.data.registry[param.eth_address] = counter

        encode_nat_lambda = sp.compute(RLP.Lambda.encode_nat)
        with_length_prefix_lambda = sp.compute(RLP.Lambda.with_length_prefix)
        encode_list_lambda = sp.compute(RLP.Lambda.encode_list)

        # Encode payload
        rlp_eth_address = with_length_prefix_lambda(param.eth_address)
        rlp_amount = encode_nat_lambda(param.amount)
        rlp_counter = encode_nat_lambda(counter)
        key = encode_list_lambda([rlp_eth_address, rlp_counter])
        payload = encode_list_lambda([rlp_eth_address, rlp_amount, rlp_counter])

        # Prepare message
        contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, self.data.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_CONTRACT)

        # Emit unwrap operation
        state_param = sp.record(key=key, value=payload)
        sp.transfer(state_param, sp.mutez(0), contract)

        # Burn tokens
        burn_param = sp.record(
            from_       = sp.sender,
            token_id    = 0,
            amount      = param.amount,
        )
        sp.transfer([burn_param], sp.mutez(0), burn_method)

    @sp.entry_point(parameter_type=Type.WrapArgument)
    def wrap(self, param):
        mint_method = Inlined.getMintEntrypoint(self.data.asset_address)

        decode_nat_lambda = sp.compute(RLP.Lambda.decode_nat)

        # Compute storage slot
        destination = sp.compute(param.destination)
        nonce = sp.compute(self.data.ethereum_nonce.get(destination, default_value = 0) + 1)
        # Increase nonce
        self.data.ethereum_nonce[destination] = nonce

        # Compute the storage slot for the ethereum proof
        storage_slot = Inlined.computeStorageSlot(destination, nonce)

        # Validate proof and extract storage value (The amount to be wrapped)
        rlp_amount = sp.view(
            "validate_storage_proof",
            self.data.proof_validator,
            sp.set_type_expr(
                sp.record(
                    block_number=param.block_number,
                    account=self.data.eth_bridge_address,
                    account_proof_rlp=param.account_proof_rlp,
                    storage_slot=storage_slot,
                    storage_proof_rlp=param.storage_proof_rlp,
                ),
                ValidatiorInterface.Validate_storage_proof_argument,
            ),
            t=sp.TBytes,
        ).open_some(Error.INVALID_VIEW)

        # Decode the amount
        amount = decode_nat_lambda(rlp_amount)

        # Mint tokens
        sp.transfer([sp.record(to_=destination, amount=amount)], sp.mutez(0), mint_method)
