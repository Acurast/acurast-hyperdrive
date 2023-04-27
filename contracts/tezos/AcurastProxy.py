# --------------------------------------------------------------------------
# This contract implements the acurast protocol on Tezos blockchain.
#
# It allows contracts to interact with Acurast chain from Tezos.
# --------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type as IBCF_Aggregator_Type
from contracts.tezos.libs.utils import RLP, Bytes, Decorator
from contracts.tezos.MMR_Validator import (
    Type as MMR_Validator_Type,
    Error as MMR_Validator_Error,
)
from contracts.tezos.AcurastConsumer import (
    Type as AcurastConsumer_Type,
    Entrypoint as AcurastConsumer_Entrypoint,
)


class Error:
    INVALID_CONTRACT = "INVALID_CONTRACT"
    INVALID_STATE_CONTRACT = "INVALID_STATE_CONTRACT"
    INVALID_CONSUMER_CONTRACT = "INVALID_CONSUMER_CONTRACT"
    INVALID_VIEW = "INVALID_VIEW"
    NOT_GOVERNANCE = "NOT_GOVERNANCE"
    OUTGOING_ACTION_NOT_SUPPORTED = "OUTGOING_ACTION_NOT_SUPPORTED"
    INGOING_ACTION_NOT_SUPPORTED = "INGOING_ACTION_NOT_SUPPORTED"
    COULD_NOT_UNPACK = "COULD_NOT_UNPACK"
    CANNOT_DECODE_ACTION = "CANNOT_DECODE_ACTION"
    CANNOT_PARSE_ACTION_STORAGE = "CANNOT_PARSE_ACTION_STORAGE"
    JOB_UNKNOWN = "JOB_UNKNOWN"
    UNEXPECTED_STORAGE_VERSION = "UNEXPECTED_STORAGE_VERSION"
    INVALID_PROOF = "INVALID_PROOF"
    NOT_JOB_PROCESSOR = "NOT_JOB_PROCESSOR"


class Type:
    # Outgoing actions
    RegisterJobAction = sp.TRecord(
        allowedSources=sp.TOption(sp.TSet(sp.TBytes)),
        allowOnlyVerifiedSources=sp.TBool,
        destination=sp.TAddress,
        extra=sp.TRecord(
            requirements=sp.TRecord(
                slots=sp.TNat,
                reward=sp.TBytes,
                minReputation=sp.TOption(sp.TNat),
                instantMatch=sp.TOption(
                    sp.TSet(sp.TRecord(source=sp.TBytes, startDelay=sp.TNat))
                ),
            ).right_comb(),
            expectedFulfillmentFee=sp.TNat,
        ).right_comb(),
        requiredModules=sp.TSet(sp.TNat),
        script=sp.TBytes,
        schedule=sp.TRecord(
            duration=sp.TNat,
            startTime=sp.TNat,
            endTime=sp.TNat,
            interval=sp.TNat,
            maxStartDelay=sp.TNat,
        ).right_comb(),
        memory=sp.TNat,
        networkRequests=sp.TNat,
        storage=sp.TNat,
    ).right_comb()

    # Ingoing actions
    AssignProcessor = sp.TRecord(
        job_id=sp.TNat,
        processor_address=sp.TAddress,
    ).right_comb()

    # Storage
    JobInformation = sp.TRecord(
        destination=sp.TAddress, processors=sp.TSet(sp.TAddress)
    )
    JobInformationIndex = sp.TBigMap(sp.TNat, JobInformation)
    ActionStorage = sp.TRecord(data=sp.TBytes, version=sp.TNat).right_comb()

    OutgoingContext = sp.TRecord(action_id=sp.TNat, job_information=JobInformationIndex)
    OutgoingActionLambdaArg = sp.TRecord(
        merkle_aggregator=sp.TAddress,
        context=OutgoingContext,
        payload=sp.TBytes,
        storage=ActionStorage,
    ).right_comb()
    OutgoingActionLambdaReturn = sp.TRecord(
        context=OutgoingContext, new_action_storage=ActionStorage
    ).right_comb()
    OutgoingActionLambda = sp.TRecord(
        function=sp.TLambda(
            OutgoingActionLambdaArg, OutgoingActionLambdaReturn, with_operations=True
        ),
        storage=ActionStorage,
    ).right_comb()

    IngoingContext = sp.TRecord(action_id=sp.TNat, job_information=JobInformationIndex)
    IngoingActionLambdaArg = sp.TRecord(
        context=IngoingContext,
        payload=sp.TBytes,
        storage=ActionStorage,
    ).right_comb()
    IngoingActionLambdaReturn = sp.TRecord(
        context=IngoingContext, new_action_storage=ActionStorage
    ).right_comb()
    IngoingActionLambda = sp.TRecord(
        function=sp.TLambda(
            IngoingActionLambdaArg, IngoingActionLambdaReturn, with_operations=True
        ),
        storage=ActionStorage,
    ).right_comb()

    # Entrypoint
    SendActionsArgument = sp.TList(
        sp.TRecord(kind=sp.TString, payload=sp.TBytes).right_comb()
    )

    ReceiveActionsArgument = sp.TRecord(
        snapshot=sp.TNat,
        mmr_size=sp.TNat,
        leaves=sp.TList(
            sp.TRecord(
                # Mountain specific index from top to bottom
                k_index=sp.TNat,
                # The general position in the tree
                mmr_pos=sp.TNat,
                # Encoded message
                data=sp.TBytes,
            ).right_comb()
        ),
        proof=sp.TList(sp.TBytes),
    ).right_comb()

    FulfillArgument = sp.TRecord(job_id=sp.TNat, payload=sp.TBytes).right_comb()

    ConfigureArgument = sp.TList(
        sp.TVariant(
            update_governance_address=sp.TAddress,
            update_proof_validator=sp.TAddress,
            update_merkle_aggregator=sp.TAddress,
            update_outgoing_actions=sp.TList(
                sp.TVariant(
                    add=sp.TRecord(kind=sp.TString, function=OutgoingActionLambda),
                    remove=sp.TString,
                ).right_comb()
            ),
            update_ingoing_actions=sp.TList(
                sp.TVariant(
                    add=sp.TRecord(kind=sp.TString, function=IngoingActionLambda),
                    remove=sp.TString,
                ).right_comb()
            ),
        ).right_comb()
    )

    AcurastMessage = sp.TRecord(
        ingoing_action_id=sp.TNat, kind=sp.TString, payload=sp.TBytes
    )


class Inlined:
    @staticmethod
    def failIfNotGovernance(self):
        """
        This method when used, ensures that only the governance address is allowed to call a given entrypoint
        """
        sp.verify(
            self.data.config.governance_address == sp.sender, Error.NOT_GOVERNANCE
        )


class OutgoingActionKind:
    REGISTER_JOB = "REGISTER_JOB"


class IngoingActionKind:
    ASSIGN_JOB_PROCESSOR = "ASSIGN_JOB_PROCESSOR"


class OutgoingActionLambda:
    @Decorator.generate_lambda(with_operations=True)
    def register_job(arg):
        sp.set_type(arg, Type.OutgoingActionLambdaArg)

        # This lambda expects the storage to be on version ONE => 1
        sp.verify(arg.storage.version == 1, Error.UNEXPECTED_STORAGE_VERSION)

        StorageType = sp.TRecord(job_id_seq=sp.TNat)
        storage = sp.compute(
            sp.unpack(arg.storage.data, StorageType).open_some(
                Error.CANNOT_PARSE_ACTION_STORAGE
            )
        )
        job_id = sp.compute(storage.job_id_seq + 1)

        action = sp.compute(
            sp.unpack(arg.payload, Type.RegisterJobAction).open_some(
                Error.COULD_NOT_UNPACK
            )
        )

        # Make sure that the destination is compatible
        sp.compute(
            sp.contract(
                AcurastConsumer_Type.Fulfill,
                action.destination,
                AcurastConsumer_Entrypoint.Fulfill,
            ).open_some(Error.INVALID_CONSUMER_CONTRACT)
        )

        # Index the job information
        context = sp.local("context", arg.context)
        context.value.job_information[job_id] = sp.record(
            destination=action.destination, processors=sp.set()
        )

        # Prepare acurast action
        action_with_job_id = sp.set_type_expr(
            sp.record(
                job_id=job_id,
                requiredModules=action.requiredModules,
                script=action.script,
                allowedSources=action.allowedSources,
                allowOnlyVerifiedSources=action.allowOnlyVerifiedSources,
                schedule=action.schedule,
                memory=action.memory,
                networkRequests=action.networkRequests,
                storage=action.storage,
                extra=action.extra,
            ),
            sp.TRecord(
                job_id=sp.TNat,
                allowedSources=sp.TOption(sp.TSet(sp.TBytes)),
                allowOnlyVerifiedSources=sp.TBool,
                extra=sp.TRecord(
                    requirements=sp.TRecord(
                        slots=sp.TNat,
                        reward=sp.TBytes,
                        minReputation=sp.TOption(sp.TNat),
                        instantMatch=sp.TOption(
                            sp.TSet(sp.TRecord(source=sp.TBytes, startDelay=sp.TNat))
                        ),
                    ).right_comb(),
                    expectedFulfillmentFee=sp.TNat,
                ).right_comb(),
                requiredModules=sp.TSet(sp.TNat),
                script=sp.TBytes,
                schedule=sp.TRecord(
                    duration=sp.TNat,
                    startTime=sp.TNat,
                    endTime=sp.TNat,
                    interval=sp.TNat,
                    maxStartDelay=sp.TNat,
                ).right_comb(),
                memory=sp.TNat,
                networkRequests=sp.TNat,
                storage=sp.TNat,
            ).right_comb(),
        )

        # Get origin
        origin = sp.compute(sp.sender)

        value = sp.pack(
            (OutgoingActionKind.REGISTER_JOB, origin, sp.pack(action_with_job_id))
        )
        key = sp.pack(context.value.action_id)
        state_param = sp.record(key=key, value=value)
        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, arg.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_STATE_CONTRACT)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(
            sp.record(
                context=context.value,
                new_action_storage=sp.record(
                    version=arg.storage.version,
                    data=sp.pack(sp.record(job_id_seq=job_id)),
                ),
            )
        )


class IngoingActionLambda:
    @Decorator.generate_lambda(with_operations=True)
    def assign_processor(arg):
        sp.set_type(arg, Type.IngoingActionLambdaArg)

        context = sp.local("context", arg.context)

        unpack_result = sp.compute(sp.unpack(arg.payload, Type.AssignProcessor))
        with sp.if_(unpack_result.is_some()):
            action = sp.compute(unpack_result.open_some(Error.COULD_NOT_UNPACK))

            # Update the processor list for the given job
            context.value.job_information[action.job_id].processors.add(
                action.processor_address
            )

        sp.result(sp.record(context=context.value, new_action_storage=arg.storage))


class AcurastProxy(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                config=sp.TRecord(
                    governance_address=sp.TAddress,
                    merkle_aggregator=sp.TAddress,
                    proof_validator=sp.TAddress,
                    outgoing_actions=sp.TBigMap(sp.TString, Type.OutgoingActionLambda),
                    ingoing_actions=sp.TBigMap(sp.TString, Type.IngoingActionLambda),
                ).right_comb(),
                outgoing_seq_id=sp.TNat,
                outgoing_registry=sp.TBigMap(sp.TNat, sp.TNat),
                ingoing_seq_id=sp.TNat,
                job_information=Type.JobInformationIndex,
            )
        )

    @sp.entry_point(parameter_type=Type.SendActionsArgument)
    def send_actions(self, arg):
        with sp.for_("action", arg) as action:
            # Get action lambda
            # - Fail with "OUTGOING_ACTION_NOT_SUPPORTED" if actions is not known
            action_lambda = self.data.config.outgoing_actions.get(
                action.kind, message=Error.OUTGOING_ACTION_NOT_SUPPORTED
            )

            # Process action
            self.data.outgoing_seq_id += 1
            self.data.outgoing_registry[self.data.outgoing_seq_id] = sp.level
            lambda_argument = sp.record(
                context=sp.record(
                    action_id=self.data.outgoing_seq_id,
                    job_information=self.data.job_information,
                ),
                merkle_aggregator=self.data.config.merkle_aggregator,
                payload=action.payload,
                storage=action_lambda.storage,
            )
            result = sp.compute(action_lambda.function(lambda_argument))

            # Commit storage changes
            self.data.job_information = result.context.job_information
            self.data.config.outgoing_actions[
                action.kind
            ].storage = result.new_action_storage

    @sp.entry_point(parameter_type=Type.ReceiveActionsArgument)
    def receive_actions(self, arg):
        # Validate proof
        is_valid = sp.view(
            "verify_proof",
            self.data.config.proof_validator,
            sp.set_type_expr(
                sp.record(
                    snapshot=arg.snapshot,
                    mmr_size=arg.mmr_size,
                    leaves=arg.leaves.map(
                        lambda leaf: sp.record(
                            k_index=leaf.k_index,
                            mmr_pos=leaf.mmr_pos,
                            hash=sp.keccak(leaf.data),
                        )
                    ),
                    proof=arg.proof,
                ),
                MMR_Validator_Type.Verify_proof_argument,
            ),
            t=sp.TBool,
        ).open_some(Error.INVALID_VIEW)

        # Fail if proof is invalid
        sp.verify(is_valid, Error.INVALID_PROOF)

        # Reaching this line, means that the proof is valid
        # Now, process each action
        with sp.for_("leaf", arg.leaves) as leaf:
            # Decode leaf data TO an action
            action = sp.compute(
                sp.unpack(leaf.data, t=Type.AcurastMessage).open_some(
                    (Error.CANNOT_DECODE_ACTION, leaf.data)
                )
            )

            # Ensure messages are processed sequentially
            sp.verify(action.ingoing_action_id == self.data.ingoing_seq_id)
            # The id coming from acurast starts on 0
            self.data.ingoing_seq_id += 1

            # Get ingoing action lambda
            # - Fail with "INGOING_ACTION_NOT_SUPPORTED" if actions is not known
            action_lambda = self.data.config.ingoing_actions.get(
                action.kind, message=Error.INGOING_ACTION_NOT_SUPPORTED
            )

            lambda_argument = sp.record(
                context=sp.record(
                    action_id=self.data.ingoing_seq_id,
                    job_information=self.data.job_information,
                ),
                payload=action.payload,
                storage=action_lambda.storage,
            )
            result = sp.compute(action_lambda.function(lambda_argument))

            # Commit storage changes
            self.data.job_information = result.context.job_information
            self.data.config.ingoing_actions[
                action.kind
            ].storage = result.new_action_storage

    @sp.entry_point(parameter_type=Type.FulfillArgument)
    def fulfill(self, arg):
        # TODO: Handle fulfillment
        # - Maybe report the fulfillment to acurast
        # - Pay processor

        # Get target address
        job_information = self.data.job_information.get(
            arg.job_id, message=Error.JOB_UNKNOWN
        )

        sp.verify(
            job_information.processors.contains(sp.sender), Error.NOT_JOB_PROCESSOR
        )

        # Pass fulfillment to target contract
        target_contract = sp.contract(
            AcurastConsumer_Type.Fulfill,
            job_information.destination,
            AcurastConsumer_Entrypoint.Fulfill,
        ).open_some(Error.INVALID_CONTRACT)
        sp.transfer(arg, sp.mutez(0), target_contract)

    @sp.entry_point(parameter_type=Type.ConfigureArgument)
    def configure(self, actions):
        # Only allowed addresses can call this entry point
        Inlined.failIfNotGovernance(self)

        # Perform actions
        with sp.for_("action", actions) as action:
            with action.match_cases() as action:
                with action.match("update_governance_address") as governance_address:
                    self.data.config.governance_address = governance_address
                with action.match("update_merkle_aggregator") as aggregator_address:
                    self.data.config.merkle_aggregator = aggregator_address
                with action.match("update_proof_validator") as validator_address:
                    self.data.config.proof_validator = validator_address
                with action.match("update_outgoing_actions") as update_outgoing_actions:
                    with sp.for_("updates", update_outgoing_actions) as updates:
                        with updates.match_cases() as action_kind:
                            with action_kind.match("add") as action_to_add:
                                self.data.config.outgoing_actions[
                                    action_to_add.kind
                                ] = action_to_add.function
                            with action_kind.match("remove") as action_to_remove:
                                del self.data.config.outgoing_actions[action_to_remove]
                with action.match("update_ingoing_actions") as update_ingoing_actions:
                    with sp.for_("updates", update_ingoing_actions) as updates:
                        with updates.match_cases() as action_kind:
                            with action_kind.match("add") as action_to_add:
                                self.data.config.ingoing_actions[
                                    action_to_add.kind
                                ] = action_to_add.function
                            with action_kind.match("remove") as action_to_remove:
                                del self.data.config.ingoing_actions[action_to_remove]
