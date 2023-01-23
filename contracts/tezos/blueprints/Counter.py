import smartpy as sp

from contracts.tezos.libs.utils import EvmStorage


class Constant:
    EVM_ACTION_REGISTRY_INDEX = sp.bytes(
        "0x0000000000000000000000000000000000000000000000000000000000000001"
    )


class Error:
    INVALID_VIEW = "INVALID_VIEW"
    INVALID_ACTION = "INVALID_ACTION"


class Type:
    Validate_storage_proof_argument = sp.TRecord(
        account=sp.TBytes,
        block_number=sp.TNat,
        account_proof_rlp=sp.TBytes,
        storage_slot=sp.TBytes,
        storage_proof_rlp=sp.TBytes,
    ).right_comb()
    ActionArgument = sp.TRecord(
        block_number=sp.TNat,
        account_proof_rlp=sp.TBytes,
        action_proof_rlp=sp.TBytes,
    ).right_comb()


class IBCF_Client(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                ibcf=sp.TRecord(
                    action_counter=sp.TNat,
                    proof_validator=sp.TAddress,
                    evm_address=sp.TBytes,
                ),
                performed_actions=sp.TList(sp.TString),
            )
        )

    @sp.entry_point(parameter_type=Type.ActionArgument)
    def perform(self, param):
        write_uint_slot_lambda = sp.compute(sp.build_lambda(EvmStorage.write_uint_slot))
        decode_string_lambda = sp.compute(sp.build_lambda(EvmStorage.read_string_slot))

        # New action, increase action counter
        self.data.ibcf.action_counter += 1

        # Compute the storage slot for the proof
        action_counter_evm_storage_slot = write_uint_slot_lambda(
            self.data.ibcf.action_counter
        )
        action_slot = sp.compute(
            sp.keccak(
                action_counter_evm_storage_slot + Constant.EVM_ACTION_REGISTRY_INDEX
            )
        )

        # Validate proof and extract storage value (The action to be performed)
        rlp_action = sp.view(
            "validate_storage_proof",
            self.data.ibcf.proof_validator,
            sp.set_type_expr(
                sp.record(
                    block_number=param.block_number,
                    account=self.data.ibcf.evm_address,
                    account_proof_rlp=param.account_proof_rlp,
                    storage_slot=action_slot,
                    storage_proof_rlp=param.action_proof_rlp,
                ),
                Type.Validate_storage_proof_argument,
            ),
            t=sp.TBytes,
        ).open_some(Error.INVALID_VIEW)

        # Decode action
        action = decode_string_lambda(rlp_action)

        self.data.performed_actions.push(action)
