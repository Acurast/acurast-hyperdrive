# -----------------------------------------------------------------------------
# This contract implements a crowdfunding blueprint for a cross-chain protocol.
#
# It allows users to participate in a Tezos Crowdfunding from Ethereum.
# -----------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.IBCF_Eth_Validator import Type as ValidatorInterface
from contracts.tezos.libs.utils import RLP, Bytes, EvmStorage


class Constant:
    FUNDER_INDEX = sp.bytes(
        "0x0000000000000000000000000000000000000000000000000000000000000001"
    )
    AMOUNT_INDEX = sp.bytes(
        "0x0000000000000000000000000000000000000000000000000000000000000002"
    )


class Error:
    INVALID_VIEW = "INVALID_VIEW"
    ALREADY_PROCESSED = "ALREADY_PROCESSED"


class Type:
    FundingFromEthArgument = sp.TRecord(
        block_number=sp.TNat,
        nonce=sp.TNat,
        account_proof_rlp=sp.TBytes,
        funder_proof_rlp=sp.TBytes,
        amount_proof_rlp=sp.TBytes,
    ).right_comb()


class Inlined:
    @staticmethod
    def computeStorageSlots(nonce):
        funder_slot = sp.keccak(nonce + Constant.FUNDER_INDEX)
        amount_slot = sp.keccak(nonce + Constant.AMOUNT_INDEX)
        return (funder_slot, amount_slot)


class IBCF_Crowdfunding(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                ibcf=sp.TRecord(
                    nonce=sp.TBigMap(sp.TNat, sp.TUnit),
                    proof_validator=sp.TAddress,
                    evm_address=sp.TBytes,
                ),
                recipient=sp.TAddress,
                # The storage below intentionally uses map instead of big_map for demonstration purposes.
                tezos_funding=sp.TMap(sp.TAddress, sp.TMutez),
                eth_funding=sp.TMap(sp.TBytes, sp.TNat),
            )
        )

    @sp.entry_point(parameter_type=sp.TUnit)
    def default(self):
        self.data.tezos_funding[sp.sender] = (
            self.data.tezos_funding.get(sp.sender, sp.tez(0)) + sp.amount
        )
        sp.send(self.data.recipient, sp.amount)

    @sp.entry_point(parameter_type=Type.FundingFromEthArgument)
    def funding_from_eth(self, param):
        decode_nat_lambda = sp.compute(RLP.Lambda.decode_nat())
        without_length_prefix = sp.compute(RLP.Lambda.without_length_prefix())
        write_uint_slot = sp.compute(sp.build_lambda(EvmStorage.write_uint_slot))

        # Verify that wrap was not yet processed, fail otherwise
        sp.verify(~self.data.ibcf.nonce.contains(param.nonce), Error.ALREADY_PROCESSED)
        # Set nonce as processed
        self.data.ibcf.nonce[param.nonce] = sp.unit

        # Compute the storage slot for the ethereum proof
        (funder_slot, amount_slot) = Inlined.computeStorageSlots(
            write_uint_slot(param.nonce)
        )

        # Validate proof and extract storage value (The funder address and the amount)
        rlp_funder = sp.view(
            "validate_storage_proof",
            self.data.ibcf.proof_validator,
            sp.set_type_expr(
                sp.record(
                    block_number=param.block_number,
                    account=self.data.ibcf.evm_address,
                    account_proof_rlp=param.account_proof_rlp,
                    storage_slot=funder_slot,
                    storage_proof_rlp=param.funder_proof_rlp,
                ),
                ValidatorInterface.Validate_storage_proof_argument,
            ),
            t=sp.TBytes,
        ).open_some(Error.INVALID_VIEW)
        rlp_amount = sp.view(
            "validate_storage_proof",
            self.data.ibcf.proof_validator,
            sp.set_type_expr(
                sp.record(
                    block_number=param.block_number,
                    account=self.data.ibcf.evm_address,
                    account_proof_rlp=param.account_proof_rlp,
                    storage_slot=amount_slot,
                    storage_proof_rlp=param.amount_proof_rlp,
                ),
                ValidatorInterface.Validate_storage_proof_argument,
            ),
            t=sp.TBytes,
        ).open_some(Error.INVALID_VIEW)

        # Decode funder address and amount
        funder = without_length_prefix(rlp_funder)
        amount = decode_nat_lambda(sp.compute(rlp_amount))

        self.data.eth_funding[funder] = self.data.eth_funding.get(funder, 0) + amount
