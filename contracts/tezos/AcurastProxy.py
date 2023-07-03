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


class Constants:
    REVEAL_COST = sp.mutez(370)


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
    PAUSED = "CONTRACT_PAUSED"
    CANNOT_FINALIZE_JOB = "CANNOT_FINALIZE_JOB"
    CANNOT_CANCEL_JOB = "CANNOT_CANCEL_JOB"
    NOT_JOB_CREATOR = "NOT_JOB_CREATOR"


class Acurast_Token_Interface:
    BurnMintTokens = sp.TList(
        sp.TRecord(
            owner=sp.TAddress,
            amount=sp.TNat,
        ).layout(("owner", "amount"))
    )


class Job_Status:
    # Status after a job got registered.
    Open = 0
    # Status after a valid match for a job got submitted.
    Matched = 1
    # Status after all processors have acknowledged the job.
    Assigned = 2
    # Status when a job has been finalized or cancelled
    FinalizedOrCancelled = 3


class Type:
    # Outgoing actions
    RegisterJobAction = sp.TRecord(
        allowedSources=sp.TOption(sp.TSet(sp.TBytes)),
        allowOnlyVerifiedSources=sp.TBool,
        destination=sp.TAddress,
        extra=sp.TRecord(
            requirements=sp.TRecord(
                slots=sp.TNat,
                reward=sp.TNat,
                minReputation=sp.TOption(sp.TNat),
                instantMatch=sp.TOption(
                    sp.TSet(sp.TRecord(source=sp.TBytes, startDelay=sp.TNat))
                ),
            ).right_comb(),
            expectedFulfillmentFee=sp.TMutez,
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

    FinalizeJob = sp.TRecord(
        job_id=sp.TNat,
        unused_reward=sp.TNat,
    ).right_comb()

    # Storage
    JobInformation = sp.TRecord(
        creator=sp.TAddress,
        destination=sp.TAddress,
        processors=sp.TSet(sp.TAddress),
        expected_fullfilment_fee=sp.TMutez,
        remaining_fee=sp.TMutez,
        maximum_reward=sp.TNat,
        slots=sp.TNat,
        status=sp.TNat,  # 0 - submitted, 1 - Assigned, 2 - Finalized/Cancelled,
        startTime=sp.TNat,
        endTime=sp.TNat,
        interval=sp.TNat,
        abstract=sp.TBytes,  # Abstract data, this field can be used to add new parameters to the job information structure after the contract has been deployed.
    )
    JobInformationIndex = sp.TBigMap(sp.TNat, JobInformation)
    ActionStorage = sp.TBytes

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

    Storage = sp.TRecord(
        config=sp.TRecord(
            governance_address=sp.TAddress,
            merkle_aggregator=sp.TAddress,
            proof_validator=sp.TAddress,
            outgoing_actions=sp.TBigMap(sp.TString, OutgoingActionLambda),
            ingoing_actions=sp.TBigMap(sp.TString, IngoingActionLambda),
            paused=sp.TBool,
        ).right_comb(),
        outgoing_seq_id=sp.TNat,
        outgoing_registry=sp.TBigMap(sp.TNat, sp.TNat),
        ingoing_seq_id=sp.TNat,
        job_information=JobInformationIndex,
    )

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
            set_paused=sp.TBool,
            update_storage=sp.TLambda(Storage, Storage),
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

    @staticmethod
    def failIfPaused(self):
        """
        This method when used, ensures that a given entrypoint can only be called when the contract is not paused
        """
        sp.verify(~self.data.config.paused, Error.PAUSED)

    @staticmethod
    def compute_execution_count(startTime, endTime, interval):
        return sp.compute(
            sp.as_nat(endTime - startTime, message="INVALID_SCHEDULE") / interval
        )

    @staticmethod
    def compute_maximum_fees(execution_count, slots, expected_fullfilment_fee):
        return sp.compute(
            sp.mul(slots * execution_count, expected_fullfilment_fee)
            + sp.mul(slots, Constants.REVEAL_COST)
        )

    @staticmethod
    def compute_maximum_reward(execution_count, slots, reward_per_execution):
        return sp.compute(slots * execution_count * reward_per_execution)


class OutgoingActionKind:
    FINALIZE_JOB = "FINALIZE_JOB"
    DEREGISTER_JOB = "DEREGISTER_JOB"
    REGISTER_JOB = "REGISTER_JOB"
    TELEPORT_ACRST = "TELEPORT_ACRST"


class IngoingActionKind:
    ASSIGN_JOB_PROCESSOR = "ASSIGN_JOB_PROCESSOR"
    FINALIZE_JOB = "FINALIZE_JOB"
    NOOP = "NOOP"


class OutgoingActionLambda:
    @Decorator.generate_lambda(with_operations=True)
    def register_job(arg):
        sp.set_type(arg, Type.OutgoingActionLambdaArg)

        StorageType = sp.TRecord(job_id_seq=sp.TNat, token_address=sp.TAddress)
        storage = sp.local(
            "action_storage",
            sp.unpack(arg.storage, StorageType).open_some(
                Error.CANNOT_PARSE_ACTION_STORAGE
            ),
        )
        storage.value.job_id_seq += 1

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

        # Calculate the number of executions that fit the job schedule
        startTime = sp.compute(action.schedule.startTime)
        endTime = sp.compute(action.schedule.endTime)
        interval = sp.compute(action.schedule.interval)
        execution_count = Inlined.compute_execution_count(startTime, endTime, interval)

        # Calculate the fee required for all job executions
        slots = sp.compute(action.extra.requirements.slots)
        expected_fullfilment_fee = sp.compute(action.extra.expectedFulfillmentFee)
        expected_fee = Inlined.compute_maximum_fees(
            execution_count,
            slots,
            expected_fullfilment_fee,
        )
        sp.verify(sp.amount == expected_fee, message="INVALID_FEE_AMOUNT")

        # Calculate the total reward required to pay all executions
        reward_per_execution = action.extra.requirements.reward
        maximum_reward = Inlined.compute_maximum_reward(
            execution_count,
            slots,
            reward_per_execution,
        )

        # Get origin
        origin = sp.compute(sp.sender)

        # Prepare action
        action_payload = sp.record(
            amount=maximum_reward,
            owner=origin,
        )

        # TODO: !IMPORTANT
        # -------------------------------------
        # Remove before going to production
        acurast_token_contract = sp.contract(
            Acurast_Token_Interface.BurnMintTokens,
            storage.value.token_address,
            "mint_tokens",
        ).open_some(Error.INVALID_CONTRACT)
        call_argument = [action_payload]
        sp.transfer(call_argument, sp.mutez(0), acurast_token_contract)
        # -------------------------------------

        ## Burn the maximum reward amount that can be used by the job
        acurast_token_contract = sp.contract(
            Acurast_Token_Interface.BurnMintTokens,
            storage.value.token_address,
            "burn_tokens",
        ).open_some(Error.INVALID_CONTRACT)
        call_argument = [action_payload]
        sp.transfer(call_argument, sp.mutez(0), acurast_token_contract)

        # Index the job information
        context = sp.local("context", arg.context)
        context.value.job_information[storage.value.job_id_seq] = sp.record(
            creator=sp.sender,
            destination=action.destination,
            expected_fullfilment_fee=expected_fullfilment_fee,
            processors=sp.set(),
            remaining_fee=expected_fee,
            maximum_reward=maximum_reward,
            slots=slots,
            status=Job_Status.Open,
            startTime=startTime,
            endTime=endTime,
            interval=interval,
            abstract=sp.bytes("0x"),
        )

        # Prepare acurast action
        action_with_job_id = sp.set_type_expr(
            sp.record(
                job_id=storage.value.job_id_seq,
                requiredModules=action.requiredModules,
                script=action.script,
                allowedSources=action.allowedSources,
                allowOnlyVerifiedSources=action.allowOnlyVerifiedSources,
                schedule=action.schedule,
                memory=action.memory,
                networkRequests=action.networkRequests,
                storage=action.storage,
                extra=action.extra.requirements,
            ),
            sp.TRecord(
                job_id=sp.TNat,
                allowedSources=sp.TOption(sp.TSet(sp.TBytes)),
                allowOnlyVerifiedSources=sp.TBool,
                extra=sp.TRecord(
                    slots=sp.TNat,
                    reward=sp.TNat,
                    minReputation=sp.TOption(sp.TNat),
                    instantMatch=sp.TOption(
                        sp.TSet(sp.TRecord(source=sp.TBytes, startDelay=sp.TNat))
                    ),
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
                new_action_storage=sp.pack(storage.value),
            )
        )

    @Decorator.generate_lambda(with_operations=True)
    def deregister_job(arg):
        sp.set_type(arg, Type.OutgoingActionLambdaArg)

        job_id = sp.compute(
            sp.unpack(arg.payload, sp.TNat).open_some(Error.COULD_NOT_UNPACK)
        )

        # Get job information
        job_information = sp.compute(
            arg.context.job_information.get(job_id, message=Error.JOB_UNKNOWN),
        )

        # Verify if job can be finalized
        is_open = sp.compute(job_information.status == Job_Status.Open)
        sp.verify(is_open, Error.CANNOT_CANCEL_JOB)

        # Only the job creator can deregister the job
        origin = sp.compute(sp.sender)
        sp.verify(job_information.creator == origin, Error.NOT_JOB_CREATOR)

        value = sp.pack((OutgoingActionKind.DEREGISTER_JOB, origin, sp.pack(job_id)))
        key = sp.pack(arg.context.action_id)
        state_param = sp.record(key=key, value=value)
        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, arg.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_STATE_CONTRACT)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(
            sp.record(
                context=arg.context,
                new_action_storage=arg.storage,
            )
        )

    @Decorator.generate_lambda(with_operations=True)
    def finalize_job(arg):
        sp.set_type(arg, Type.OutgoingActionLambdaArg)

        job_ids = sp.compute(
            sp.unpack(arg.payload, sp.TSet(sp.TNat)).open_some(Error.COULD_NOT_UNPACK)
        )

        origin = sp.compute(sp.sender)
        with sp.for_("job_id", job_ids.elements()) as job_id:
            # Get job information
            job_information = sp.compute(
                arg.context.job_information.get(job_id, message=Error.JOB_UNKNOWN),
            )

            # Verify if job can be finalized
            is_open = sp.compute(job_information.status == Job_Status.Open)
            is_expired = sp.compute(
                sp.add(sp.to_int(job_information.endTime / 1000), sp.timestamp(0))
                < sp.now
            )
            sp.verify(is_open | is_expired, Error.CANNOT_FINALIZE_JOB)

            # Only the job creator can deregister the job
            sp.verify(job_information.creator == origin, Error.NOT_JOB_CREATOR)

        value = sp.pack((OutgoingActionKind.FINALIZE_JOB, origin, sp.pack(job_ids)))
        key = sp.pack(arg.context.action_id)
        state_param = sp.record(key=key, value=value)
        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, arg.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_STATE_CONTRACT)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(
            sp.record(
                context=arg.context,
                new_action_storage=arg.storage,
            )
        )

    @Decorator.generate_lambda(with_operations=True)
    def teleport_acrst(arg):
        sp.set_type(arg, Type.OutgoingActionLambdaArg)

        StorageType = sp.TAddress
        acurast_token_address = sp.compute(
            sp.unpack(arg.storage, StorageType).open_some(
                Error.CANNOT_PARSE_ACTION_STORAGE
            )
        )

        amount = sp.compute(
            sp.unpack(arg.payload, sp.TNat).open_some(Error.COULD_NOT_UNPACK)
        )

        # Get origin
        origin = sp.compute(sp.sender)

        # Prepare action
        action_payload = sp.record(
            amount=amount,
            owner=origin,
        )

        ## Burn reward on Tezos chain
        acurast_token_contract = sp.contract(
            Acurast_Token_Interface.BurnMintTokens,
            acurast_token_address,
            "burn_tokens",
        ).open_some(Error.INVALID_CONTRACT)
        call_argument = [action_payload]
        sp.transfer(call_argument, sp.mutez(0), acurast_token_contract)

        ## Emit TELEPORT_ACRST action

        value = sp.pack(
            (OutgoingActionKind.TELEPORT_ACRST, origin, sp.pack(action_payload))
        )
        key = sp.pack(arg.context.action_id)
        state_param = sp.record(key=key, value=value)
        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, arg.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_STATE_CONTRACT)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(
            sp.record(
                context=arg.context,
                new_action_storage=arg.storage,
            )
        )


class IngoingActionLambda:
    @Decorator.generate_lambda(with_operations=True)
    def noop(arg):
        sp.set_type(arg, Type.IngoingActionLambdaArg)

        sp.result(sp.record(context=arg.context, new_action_storage=arg.storage))

    @Decorator.generate_lambda(with_operations=True)
    def assign_processor(arg):
        sp.set_type(arg, Type.IngoingActionLambdaArg)

        context = sp.local("context", arg.context)

        unpack_result = sp.compute(sp.unpack(arg.payload, Type.AssignProcessor))
        with sp.if_(unpack_result.is_some()):
            action = sp.compute(unpack_result.open_some(Error.COULD_NOT_UNPACK))
            job_information = sp.local(
                "job_information", context.value.job_information[action.job_id]
            )

            # Update the processor list for the given job
            job_information.value.processors.add(action.processor_address)

            # Send initial fees to the processor (the processor may need a reveal)
            initial_fee = sp.compute(
                job_information.value.expected_fullfilment_fee + Constants.REVEAL_COST
            )
            job_information.value.remaining_fee = (
                job_information.value.remaining_fee - initial_fee
            )
            sp.send(
                action.processor_address, initial_fee, message=Error.INVALID_CONTRACT
            )

            # Updated job status
            with sp.if_(
                sp.len(job_information.value.processors) == job_information.value.slots
            ):
                job_information.value.status = Job_Status.Assigned

            # Update job information
            context.value.job_information[action.job_id] = job_information.value

        sp.result(sp.record(context=context.value, new_action_storage=arg.storage))

    @Decorator.generate_lambda(with_operations=True)
    def finalize_job(arg):
        sp.set_type(arg, Type.IngoingActionLambdaArg)

        StorageType = sp.TAddress
        acurast_token_address = sp.compute(
            sp.unpack(arg.storage, StorageType).open_some(
                Error.CANNOT_PARSE_ACTION_STORAGE
            )
        )

        context = sp.local("context", arg.context)

        unpack_result = sp.compute(sp.unpack(arg.payload, Type.FinalizeJob))
        with sp.if_(unpack_result.is_some()):
            action = sp.compute(unpack_result.open_some(Error.COULD_NOT_UNPACK))
            job_information = sp.local(
                "job_information", context.value.job_information[action.job_id]
            )

            # Update job status
            job_information.value.status = Job_Status.FinalizedOrCancelled

            # Send unused fees to the job creator
            with sp.if_(job_information.value.remaining_fee > sp.mutez(0)):
                sp.send(
                    job_information.value.creator,
                    job_information.value.remaining_fee,
                    message=Error.INVALID_CONTRACT,
                )
                job_information.value.remaining_fee = sp.mutez(0)

            # Mint unused rewards back to the job creator
            sp.verify(
                action.unused_reward <= job_information.value.maximum_reward,
                "ABOVE_MAXIMUM_REWARD",
            )
            acurast_token_contract = sp.contract(
                Acurast_Token_Interface.BurnMintTokens,
                acurast_token_address,
                "mint_tokens",
            ).open_some(Error.INVALID_CONTRACT)
            mint_payload = sp.record(
                amount=action.unused_reward,
                owner=job_information.value.creator,
            )
            call_argument = [mint_payload]
            sp.transfer(call_argument, sp.mutez(0), acurast_token_contract)

            # Update job information
            context.value.job_information[action.job_id] = job_information.value

        sp.result(sp.record(context=context.value, new_action_storage=arg.storage))


class AcurastProxy(sp.Contract):
    def __init__(self):
        self.init_type(Type.Storage)

    @sp.entry_point(parameter_type=Type.SendActionsArgument)
    def send_actions(self, arg):
        Inlined.failIfPaused(self)

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
        # Get job information
        job_information = sp.local(
            "job_information",
            self.data.job_information.get(arg.job_id, message=Error.JOB_UNKNOWN),
        )

        # Verify if sender is assigned to the job
        sp.verify(
            job_information.value.processors.contains(sp.sender),
            Error.NOT_JOB_PROCESSOR,
        )

        # Re-fill processor fees
        job_information.value.remaining_fee -= (
            job_information.value.expected_fullfilment_fee
        )
        # Forbidden to credit 0ꜩ to a contract without code.
        with sp.if_(job_information.value.expected_fullfilment_fee > sp.mutez(0)):
            sp.send(
                sp.sender,
                job_information.value.expected_fullfilment_fee,
                message=Error.INVALID_CONTRACT,
            )

        # Pass fulfillment to target contract
        target_contract = sp.contract(
            AcurastConsumer_Type.Fulfill,
            job_information.value.destination,
            AcurastConsumer_Entrypoint.Fulfill,
        ).open_some(Error.INVALID_CONTRACT)
        sp.transfer(arg, sp.mutez(0), target_contract)

        self.data.job_information[arg.job_id] = job_information.value

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
                with action.match("set_paused") as paused:
                    self.data.config.paused = paused
                with action.match("update_storage") as lamb:
                    self.data = lamb(self.data)
