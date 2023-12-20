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
import contracts.tezos.libs.fa2_lib as FA2

class Market:
    ASSET_ADDRESS = sp.address("KT1XRPEPXbZK25r3Htzp2o1x7xdMMmfocKNW") # https://better-call.dev/mainnet/KT1XRPEPXbZK25r3Htzp2o1x7xdMMmfocKNW
    ASSET_ID = 0 # uUSD

    def compute_swap_price(expected_acurast_amount):
        # 1B cACU (12 decimals) ||== 65M uUSD (12 decimals)
        ratio = sp.record(
            numerator = 65,
            denominator = 1000
        )
        # Calculate how many uusd is required to cover for the job cost
        exchange_result = sp.compute(
            sp.ediv(ratio.numerator * expected_acurast_amount, ratio.denominator).open_some("FAILED_TO_CONVERT_AMOUNT")
        )
        # Ceil the amount if the result has decimal places
        exchange_amount = sp.local("exchange_amount", sp.fst(exchange_result))
        with sp.if_(sp.snd(exchange_result) > 0):
            exchange_amount.value += 1

        return exchange_amount.value

    def refund_uusd_tokens(exchange_asset, destination, amount):
        payload = sp.record(
            from_ = sp.self_address,
            txs=[
                sp.record(
                    to_         = destination,
                    token_id    = exchange_asset.id,
                    amount      = Market.compute_swap_price(amount),
                )
            ],
        )

        token_contract = sp.contract(
            FA2.t_transfer_params,
            exchange_asset.address,
            "transfer",
        ).open_some(Error.INVALID_CONTRACT)
        call_argument = [payload]
        sp.transfer(call_argument, sp.mutez(0), token_contract)

    def pay_with_uusd_tokens(exchange_asset, amount):
        payload = sp.record(
            from_ = sp.sender,
            txs=[
                sp.record(
                    to_         = sp.self_address,
                    token_id    = exchange_asset.id,
                    amount      = Market.compute_swap_price(amount),
                )
            ],
        )

        token_contract = sp.contract(
            FA2.t_transfer_params,
            exchange_asset.address,
            "transfer",
        ).open_some(Error.INVALID_CONTRACT)
        call_argument = [payload]
        sp.transfer(call_argument, sp.mutez(0), token_contract)

class Constants:
    REVEAL_COST = sp.mutez(1200)


class Error:
    INVALID_CONTRACT = "INVALID_CONTRACT"
    INVALID_STATE_CONTRACT = "INVALID_STATE_CONTRACT"
    INVALID_CONSUMER_CONTRACT = "INVALID_CONSUMER_CONTRACT"
    INVALID_VIEW = "INVALID_VIEW"
    NOT_GOVERNANCE = "NOT_GOVERNANCE"
    OUTGOING_ACTION_NOT_SUPPORTED = "OUTGOING_ACTION_NOT_SUPPORTED"
    INCOMING_ACTION_NOT_SUPPORTED = "INCOMING_ACTION_NOT_SUPPORTED"
    COULD_NOT_UNPACK = "COULD_NOT_UNPACK"
    CANNOT_DECODE_ACTION = "CANNOT_DECODE_ACTION"
    CANNOT_PARSE_ACTION_STORAGE = "CANNOT_PARSE_ACTION_STORAGE"
    JOB_UNKNOWN = "JOB_UNKNOWN"
    UNEXPECTED_STORAGE_VERSION = "UNEXPECTED_STORAGE_VERSION"
    INVALID_PROOF = "INVALID_PROOF"
    NOT_JOB_PROCESSOR = "NOT_JOB_PROCESSOR"
    JOB_ALREADY_FINALIZED = "JOB_ALREADY_FINALIZED"
    PAUSED = "CONTRACT_PAUSED"
    CANNOT_FINALIZE_JOB = "CANNOT_FINALIZE_JOB"
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

    SetJobEnvironmentAction = sp.TRecord(
        job_id = sp.TNat,
        public_key = sp.TBytes,
        processors = sp.TMap(sp.TBytes, sp.TMap(sp.TBytes, sp.TBytes))
    ).right_comb()

    # Incoming actions
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

    Store = sp.TRecord(
        config=sp.TRecord(
            governance_address=sp.TAddress,
            merkle_aggregator=sp.TAddress,
            proof_validator=sp.TAddress,
            paused=sp.TBool,
        ).right_comb(),
        outgoing_seq_id=sp.TNat,
        outgoing_registry=sp.TBigMap(sp.TNat, sp.TNat),
        incoming_seq_id=sp.TNat,
        job_information=JobInformationIndex,
    )

    OutgoingContext = sp.TRecord(action_id=sp.TNat, store=Store)
    OutgoingActionLambdaArg = sp.TRecord(
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

    IncomingContext = sp.TRecord(action_id=sp.TNat, store=Store)
    IncomingActionLambdaArg = sp.TRecord(
        context=IncomingContext,
        payload=sp.TBytes,
        storage=ActionStorage,
    ).right_comb()
    IncomingActionLambdaReturn = sp.TRecord(
        context=IncomingContext, new_action_storage=ActionStorage
    ).right_comb()
    IncomingActionLambda = sp.TRecord(
        function=sp.TLambda(
            IncomingActionLambdaArg, IncomingActionLambdaReturn, with_operations=True
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
        outgoing_actions=sp.TBigMap(sp.TString, OutgoingActionLambda),
        incoming_actions=sp.TBigMap(sp.TString, IncomingActionLambda),
        store=Store,
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
            update_incoming_actions=sp.TList(
                sp.TVariant(
                    add=sp.TRecord(kind=sp.TString, function=IncomingActionLambda),
                    remove=sp.TString,
                ).right_comb()
            ),
            set_paused=sp.TBool,
            generic=sp.TLambda(
                sp.TUnit, sp.TUnit, with_storage="read-write", with_operations=True
            ),
        ).right_comb()
    )

    AcurastMessage = sp.TRecord(
        incoming_action_id=sp.TNat, kind=sp.TString, payload=sp.TBytes
    )


class Inlined:
    @staticmethod
    def failIfNotGovernance(self):
        """
        This method when used, ensures that only the governance address is allowed to call a given entrypoint
        """
        sp.verify(
            self.data.store.config.governance_address == sp.sender, Error.NOT_GOVERNANCE
        )

    @staticmethod
    def failIfPaused(self):
        """
        This method when used, ensures that a given entrypoint can only be called when the contract is not paused
        """
        sp.verify(~self.data.store.config.paused, Error.PAUSED)

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
    SET_JOB_ENVIRONMENT = "SET_JOB_ENVIRONMENT"
    TELEPORT_ACRST = "TELEPORT_ACRST" # TODO: remove?
    NOOP = "NOOP"

class IncomingActionKind:
    ASSIGN_JOB_PROCESSOR = "ASSIGN_JOB_PROCESSOR"
    FINALIZE_JOB = "FINALIZE_JOB"
    NOOP = "NOOP"

class OutgoingActionLambda:
    @Decorator.generate_lambda(with_operations=True)
    def noop(arg):
        sp.set_type(arg, Type.OutgoingActionLambdaArg)

        origin = sp.compute(sp.sender)

        value = sp.pack((OutgoingActionKind.NOOP, origin, sp.bytes("0x")))
        key = sp.pack(arg.context.action_id)
        state_param = sp.record(key=key, value=value)
        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument,
            arg.context.store.config.merkle_aggregator,
            "insert",
        ).open_some(Error.INVALID_STATE_CONTRACT)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(
            sp.record(
                context=arg.context,
                new_action_storage=arg.storage,
            )
        )

    @Decorator.generate_lambda(with_operations=True)
    def register_job(arg):
        sp.set_type(arg, Type.OutgoingActionLambdaArg)

        StorageType = sp.TRecord(
            job_id_seq=sp.TNat,
            token_address=sp.TAddress,
            fa2_uusd = sp.TRecord(
                address=sp.TAddress,
                id=sp.TNat
            )
        )
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

        # Pay job registration with uusd
        Market.pay_with_uusd_tokens(storage.value.fa2_uusd, maximum_reward)

        # Index the job information
        context = sp.local("context", arg.context)
        context.value.store.job_information[storage.value.job_id_seq] = sp.record(
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
            IBCF_Aggregator_Type.Insert_argument,
            context.value.store.config.merkle_aggregator,
            "insert",
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
            arg.context.store.job_information.get(job_id, message=Error.JOB_UNKNOWN),
        )

        # Only the job creator can deregister the job
        origin = sp.compute(sp.sender)
        sp.verify(job_information.creator == origin, Error.NOT_JOB_CREATOR)

        value = sp.pack((OutgoingActionKind.DEREGISTER_JOB, origin, sp.pack(job_id)))
        key = sp.pack(arg.context.action_id)
        state_param = sp.record(key=key, value=value)
        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument,
            arg.context.store.config.merkle_aggregator,
            "insert",
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
                arg.context.store.job_information.get(
                    job_id, message=Error.JOB_UNKNOWN
                ),
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
            IBCF_Aggregator_Type.Insert_argument,
            arg.context.store.config.merkle_aggregator,
            "insert",
        ).open_some(Error.INVALID_STATE_CONTRACT)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(
            sp.record(
                context=arg.context,
                new_action_storage=arg.storage,
            )
        )

    @Decorator.generate_lambda(with_operations=True)
    def set_job_environment(arg):
        sp.set_type(arg, Type.OutgoingActionLambdaArg)

        # Validate payload
        decoded_arg = sp.compute(
            sp.unpack(arg.payload, Type.SetJobEnvironmentAction).open_some(Error.COULD_NOT_UNPACK)
        )

        # Get job information
        job_information = sp.compute(
            arg.context.store.job_information.get(decoded_arg.job_id, message=Error.JOB_UNKNOWN),
        )

        # Only the job creator can deregister the job
        origin = sp.compute(sp.sender)
        sp.verify(job_information.creator == origin, Error.NOT_JOB_CREATOR)

        value = sp.pack((OutgoingActionKind.SET_JOB_ENVIRONMENT, origin, arg.payload))
        key = sp.pack(arg.context.action_id)
        state_param = sp.record(key=key, value=value)
        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument,
            arg.context.store.config.merkle_aggregator,
            "insert",
        ).open_some(Error.INVALID_STATE_CONTRACT)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(
            sp.record(
                context=arg.context,
                new_action_storage=arg.storage,
            )
        )

    # @Decorator.generate_lambda(with_operations=True)
    # def teleport_acrst(arg):
    #     sp.set_type(arg, Type.OutgoingActionLambdaArg)

    #     StorageType = sp.TAddress
    #     acurast_token_address = sp.compute(
    #         sp.unpack(arg.storage, StorageType).open_some(
    #             Error.CANNOT_PARSE_ACTION_STORAGE
    #         )
    #     )

    #     amount = sp.compute(
    #         sp.unpack(arg.payload, sp.TNat).open_some(Error.COULD_NOT_UNPACK)
    #     )

    #     # Get origin
    #     origin = sp.compute(sp.sender)

    #     # Prepare action
    #     action_payload = sp.record(
    #         amount=amount,
    #         owner=origin,
    #     )

    #     ## Burn reward on Tezos chain
    #     acurast_token_contract = sp.contract(
    #         Acurast_Token_Interface.BurnMintTokens,
    #         acurast_token_address,
    #         "burn_tokens",
    #     ).open_some(Error.INVALID_CONTRACT)
    #     call_argument = [action_payload]
    #     sp.transfer(call_argument, sp.mutez(0), acurast_token_contract)

    #     ## Emit TELEPORT_ACRST action

    #     value = sp.pack(
    #         (OutgoingActionKind.TELEPORT_ACRST, origin, sp.pack(action_payload))
    #     )
    #     key = sp.pack(arg.context.action_id)
    #     state_param = sp.record(key=key, value=value)
    #     # Add acurast action to the state merkle tree
    #     merkle_aggregator_contract = sp.contract(
    #         IBCF_Aggregator_Type.Insert_argument,
    #         arg.context.store.config.merkle_aggregator,
    #         "insert",
    #     ).open_some(Error.INVALID_STATE_CONTRACT)
    #     sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

    #     sp.result(
    #         sp.record(
    #             context=arg.context,
    #             new_action_storage=arg.storage,
    #         )
    #     )


class IncomingActionLambda:
    @Decorator.generate_lambda(with_operations=True)
    def noop(arg):
        sp.set_type(arg, Type.IncomingActionLambdaArg)

        sp.result(sp.record(context=arg.context, new_action_storage=arg.storage))

    @Decorator.generate_lambda(with_operations=True)
    def assign_processor(arg):
        sp.set_type(arg, Type.IncomingActionLambdaArg)

        context = sp.local("context", arg.context)

        unpack_result = sp.compute(sp.unpack(arg.payload, Type.AssignProcessor))
        with sp.if_(unpack_result.is_some()):
            action = sp.compute(unpack_result.open_some(Error.COULD_NOT_UNPACK))
            job_information = sp.local(
                "job_information", context.value.store.job_information[action.job_id]
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
            context.value.store.job_information[action.job_id] = job_information.value

        sp.result(sp.record(context=context.value, new_action_storage=arg.storage))

    @Decorator.generate_lambda(with_operations=True)
    def finalize_job(arg):
        sp.set_type(arg, Type.IncomingActionLambdaArg)

        StorageType = sp.TRecord(
            address=sp.TAddress,
            id=sp.TNat
        )
        uusd_asset = sp.compute(
            sp.unpack(arg.storage, StorageType).open_some(
                Error.CANNOT_PARSE_ACTION_STORAGE
            )
        )

        context = sp.local("context", arg.context)

        unpack_result = sp.compute(sp.unpack(arg.payload, Type.FinalizeJob))
        with sp.if_(unpack_result.is_some()):
            action = sp.compute(unpack_result.open_some(Error.COULD_NOT_UNPACK))
            job_information = sp.local(
                "job_information", context.value.store.job_information[action.job_id]
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

            # Refund remaining uusd
            Market.refund_uusd_tokens(uusd_asset, job_information.value.creator, action.unused_reward)

            # Update job information
            context.value.store.job_information[action.job_id] = job_information.value

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
            action_lambda = self.data.outgoing_actions.get(
                action.kind, message=Error.OUTGOING_ACTION_NOT_SUPPORTED
            )

            # Process action
            self.data.store.outgoing_seq_id += 1
            self.data.store.outgoing_registry[
                self.data.store.outgoing_seq_id
            ] = sp.level
            lambda_argument = sp.record(
                context=sp.record(
                    action_id=self.data.store.outgoing_seq_id,
                    store=self.data.store,
                ),
                payload=action.payload,
                storage=action_lambda.storage,
            )
            result = sp.compute(action_lambda.function(lambda_argument))

            # Commit storage changes
            self.data.store = result.context.store
            self.data.outgoing_actions[action.kind].storage = result.new_action_storage

    @sp.entry_point(parameter_type=Type.ReceiveActionsArgument)
    def receive_actions(self, arg):
        Inlined.failIfPaused(self)
        # Validate proof
        is_valid = sp.view(
            "verify_proof",
            self.data.store.config.proof_validator,
            sp.set_type_expr(
                sp.record(
                    snapshot=arg.snapshot,
                    mmr_size=arg.mmr_size,
                    leaves=arg.leaves.map(
                        lambda leaf: sp.record(
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
            sp.verify(action.incoming_action_id == self.data.store.incoming_seq_id)
            # The id coming from acurast starts on 0
            self.data.store.incoming_seq_id += 1

            # Get incoming action lambda
            # - Fail with "INCOMING_ACTION_NOT_SUPPORTED" if actions is not known
            action_lambda = self.data.incoming_actions.get(
                action.kind, message=Error.INCOMING_ACTION_NOT_SUPPORTED
            )

            lambda_argument = sp.record(
                context=sp.record(
                    action_id=self.data.store.incoming_seq_id,
                    store=self.data.store,
                ),
                payload=action.payload,
                storage=action_lambda.storage,
            )
            result = sp.compute(action_lambda.function(lambda_argument))

            # Commit storage changes
            self.data.store = result.context.store
            self.data.incoming_actions[action.kind].storage = result.new_action_storage

    @sp.entry_point(parameter_type=Type.FulfillArgument)
    def fulfill(self, arg):
        Inlined.failIfPaused(self)
        # Get job information
        job_information = sp.local(
            "job_information",
            self.data.store.job_information.get(arg.job_id, message=Error.JOB_UNKNOWN),
        )

        # Verify if sender is assigned to the job
        sp.verify(
            job_information.value.processors.contains(sp.sender),
            Error.NOT_JOB_PROCESSOR,
        )

        # Verify that the job has not been finalized
        sp.verify(job_information.value.status == Job_Status.FinalizedOrCancelled, Error.JOB_ALREADY_FINALIZED)

        # Re-fill processor fees
        # Forbidden to credit 0ꜩ to a contract without code.
        has_funds = job_information.value.remaining_fee >= job_information.value.expected_fullfilment_fee
        with sp.if_(has_funds & (job_information.value.expected_fullfilment_fee > sp.mutez(0))):
            job_information.value.remaining_fee -= (
               job_information.value.expected_fullfilment_fee
            )
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

        self.data.store.job_information[arg.job_id] = job_information.value

    @sp.entry_point(parameter_type=Type.ConfigureArgument)
    def configure(self, actions):
        # Only allowed addresses can call this entry point
        Inlined.failIfNotGovernance(self)

        # Perform actions
        with sp.for_("action", actions) as action:
            with action.match_cases() as action:
                with action.match("update_governance_address") as governance_address:
                    self.data.store.config.governance_address = governance_address
                with action.match("update_merkle_aggregator") as aggregator_address:
                    self.data.store.config.merkle_aggregator = aggregator_address
                with action.match("update_proof_validator") as validator_address:
                    self.data.store.config.proof_validator = validator_address
                with action.match("update_outgoing_actions") as update_outgoing_actions:
                    with sp.for_("updates", update_outgoing_actions) as updates:
                        with updates.match_cases() as action_kind:
                            with action_kind.match("add") as action_to_add:
                                self.data.outgoing_actions[
                                    action_to_add.kind
                                ] = action_to_add.function
                            with action_kind.match("remove") as action_to_remove:
                                del self.data.outgoing_actions[action_to_remove]
                with action.match("update_incoming_actions") as update_incoming_actions:
                    with sp.for_("updates", update_incoming_actions) as updates:
                        with updates.match_cases() as action_kind:
                            with action_kind.match("add") as action_to_add:
                                self.data.incoming_actions[
                                    action_to_add.kind
                                ] = action_to_add.function
                            with action_kind.match("remove") as action_to_remove:
                                del self.data.incoming_actions[action_to_remove]
                with action.match("set_paused") as paused:
                    self.data.store.config.paused = paused
                with action.match("generic") as lamb:
                    sp.compute(lamb(sp.unit))
