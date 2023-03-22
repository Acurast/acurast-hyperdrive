# --------------------------------------------------------------------------
# This contract implements the acurast protocol on Tezos blockchain.
#
# It allows contracts to interact with Acurast chain from Tezos.
# --------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type as IBCF_Aggregator_Type
from contracts.tezos.IBCF_Eth_Validator import Type as ValidatorInterface
from contracts.tezos.libs.utils import RLP, Bytes


class Error:
    INVALID_CONTRACT = "INVALID_CONTRACT"
    NOT_GOVERNANCE = "NOT_GOVERNANCE"
    ACTION_NOT_SUPPORTED = "ACTION_NOT_SUPPORTED"
    COULD_NOT_UNPACK = "COULD_NOT_UNPACK"
    CANNOT_PARSE_ACTION_STORAGE = "CANNOT_PARSE_ACTION_STORAGE"
    JOB_UNKNOWN = "JOB_UNKNOWN"
    UNEXPECTED_STORAGE_VERSION = "UNEXPECTED_STORAGE_VERSION"


class Type:
    # Actions
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
    # Storage
    JobRegistry = sp.TBigMap(
        sp.TNat,
        sp.TRecord(
            level = sp.TNat,
            metadata = RegisterJobAction,
        ).right_comb()
    )
    ActionStorage = sp.TRecord(data=sp.TBytes, version=sp.TNat).right_comb()
    ActionLambdaArg = sp.TRecord(
        action_number=sp.TNat,
        merkle_aggregator=sp.TAddress,
        payload=sp.TBytes,
        registry=JobRegistry,
        storage=ActionStorage,
    ).right_comb()
    ActionLambdaReturn = sp.TRecord(
        registry=JobRegistry, new_action_storage=ActionStorage
    ).right_comb()
    ActionLambda = sp.TRecord(
        function=sp.TLambda(ActionLambdaArg, ActionLambdaReturn, with_operations=True),
        storage=ActionStorage,
    ).right_comb()
    # Entrypoint
    PerformActionArgument = sp.TRecord(
        action=sp.TString, payload=sp.TBytes
    ).right_comb()
    FulfillArgument = sp.TRecord(jobId=sp.TNat, payload=sp.TBytes).right_comb()
    ConfigureArgument = sp.TList(
        sp.TVariant(
            update_governance_address=sp.TAddress,
            update_authorized_actions=sp.TList(
                sp.TVariant(
                    add=sp.TRecord(kind=sp.TString, function=ActionLambda),
                    remove=sp.TString,
                ).right_comb()
            ),
        ).right_comb()
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


class ActionKind:
    REGISTER_JOB = "REGISTER_JOB"


class ActionLambda:
    class Decorator:
        def action_lambda(with_operations=True, recursive=False):
            """
            A decorator that transforms a function into a Tezos Lambda
            """

            def transform(f):
                return sp.build_lambda(
                    f, with_operations=with_operations, recursive=recursive
                )

            return transform

    @Decorator.action_lambda(with_operations=True)
    def register_job(arg):
        sp.set_type(arg, Type.ActionLambdaArg)

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

        # Get origin
        origin = sp.compute(sp.sender)

        # Map the fulfillment recipient to the job
        registry = sp.local("registry", arg.registry)
        registry.value[job_id] = sp.record(
            level = sp.level,
            metadata = action,
        )

        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, arg.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_CONTRACT)
        # Emit acurast action
        action_with_job_id = sp.set_type_expr(
            sp.record(
                jobId=job_id,
                destination=action.destination,
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
                jobId=sp.TNat,
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

        value = sp.pack((ActionKind.REGISTER_JOB, origin, sp.pack(action_with_job_id)))
        key = sp.pack(arg.action_number)
        state_param = sp.record(key=key, value=value)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(
            sp.record(
                registry=registry.value,
                new_action_storage=sp.record(
                    version=arg.storage.version,
                    data=sp.pack(sp.record(job_id_seq=job_id)),
                ),
            )
        )


class AcurastProxy(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                config=sp.TRecord(
                    governance_address=sp.TAddress,
                    merkle_aggregator=sp.TAddress,
                    proof_validator=sp.TAddress,
                    authorized_actions=sp.TBigMap(sp.TString, Type.ActionLambda),
                ),
                outgoing_counter=sp.TNat,
                registry=Type.JobRegistry,
            )
        )

    @sp.entry_point(parameter_type=Type.PerformActionArgument)
    def perform_action(self, args):
        # Get action lambda
        # - Fail with "ACTION_NOT_SUPPORTED" if actions is not known
        action_lambda = self.data.config.authorized_actions.get(
            args.action, message=Error.ACTION_NOT_SUPPORTED
        )

        # Process action
        self.data.outgoing_counter += 1
        lambda_argument = sp.record(
            storage=action_lambda.storage,
            action_number=self.data.outgoing_counter,
            merkle_aggregator=self.data.config.merkle_aggregator,
            registry=self.data.registry,
            payload=args.payload,
        )
        result = sp.compute(action_lambda.function(lambda_argument))

        self.data.registry = result.registry
        self.data.config.authorized_actions[
            args.action
        ].storage = result.new_action_storage

    @sp.entry_point(parameter_type=Type.FulfillArgument)
    def fulfill(self, args):
        # TODO: Handle fulfillment
        # - Maybe report the fulfillment to acurast
        # - Pay processor

        # Get target address
        job_info = self.data.registry.get(args.jobId, message=Error.JOB_UNKNOWN)

        # Pass fulfillment to target contract
        target_contract = sp.contract(
            sp.TBytes, job_info.metadata.destination, "fulfill"
        ).open_some(Error.INVALID_CONTRACT)
        sp.transfer(args.payload, sp.mutez(0), target_contract)

    @sp.entry_point(parameter_type=Type.ConfigureArgument)
    def configure(self, actions):
        # Only allowed addresses can call this entry point
        Inlined.failIfNotGovernance(self)

        # Perform actions
        with sp.for_("action", actions) as action:
            with action.match_cases() as action:
                with action.match("update_governance_address") as governance_address:
                    self.data.config.governance_address = governance_address
                with action.match(
                    "update_authorized_actions"
                ) as update_authorized_actions:
                    with sp.for_(
                        "update_authorized_action", update_authorized_actions
                    ) as updates:
                        with updates.match_cases() as action_kind:
                            with action_kind.match("add") as action_to_add:
                                self.data.config.authorized_actions[
                                    action_to_add.kind
                                ] = action_to_add.function
                            with action_kind.match("remove") as action_to_remove:
                                del self.data.config.authorized_actions[
                                    action_to_remove
                                ]
