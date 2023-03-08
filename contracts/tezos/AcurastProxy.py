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
    JOB_UNKNOWN = "JOB_UNKNOWN"


class Type:
    # Storage
    Registry = sp.TBigMap(sp.TPair(sp.TAddress, sp.TBytes), sp.TAddress)
    ActionLambdaArg = sp.TRecord(
        action_number=sp.TNat,
        merkle_aggregator=sp.TAddress,
        registry=Registry,
        payload=sp.TBytes,
    ).right_comb()
    ActionLambdaReturn = sp.TRecord(registry=Registry).right_comb()
    ActionLambda = sp.TLambda(ActionLambdaArg, ActionLambdaReturn, with_operations=True)
    # Entrypoint
    PerformActionArgument = sp.TRecord(
        action=sp.TString, payload=sp.TBytes
    ).right_comb()
    FulfillArgument = sp.TRecord(
        requester=sp.TAddress, script=sp.TBytes, payload=sp.TBytes
    ).right_comb()
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
    # Actions
    RegisterJobAction = sp.TRecord(
        destination=sp.TAddress,
        script=sp.TBytes,
        allowedSources=sp.TOption(sp.TSet(sp.TString)),
        allowOnlyVerifiedSources=sp.TBool,
        schedule=sp.TRecord(
            duration=sp.TNat,
            startTime=sp.TNat,
            endTime=sp.TNat,
            interval=sp.TNat,
            maxStartDelay=sp.TNat,
        ),
        memory=sp.TNat,
        networkRequests=sp.TNat,
        storage=sp.TNat,
        extra=sp.TRecord(
            requirements=sp.TRecord(
                slots=sp.TNat,
                reward=sp.TBytes,
                minReputation=sp.TOption(sp.TNat),
                instantMatch=sp.TOption(
                    sp.TSet(sp.TRecord(source=sp.TString, startDelay=sp.TNat))
                ),
            ),
            expectedFulfillmentFee=sp.TNat,
        ),
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

        action = sp.compute(
            sp.unpack(arg.payload, Type.RegisterJobAction).open_some(
                Error.COULD_NOT_UNPACK
            )
        )

        # TODO: Handle registration

        # Get origin
        origin = sp.compute(sp.sender)

        # Map the fulfillment recipient to the job
        registry = sp.local("registry", arg.registry)
        registry.value[(origin, action.script)] = action.destination

        # Add acurast action to the state merkle tree
        merkle_aggregator_contract = sp.contract(
            IBCF_Aggregator_Type.Insert_argument, arg.merkle_aggregator, "insert"
        ).open_some(Error.INVALID_CONTRACT)
        # Emit acurast action
        value = sp.pack((ActionKind.REGISTER_JOB, origin, arg.payload))
        key = sp.pack(arg.action_number)
        state_param = sp.record(key=key, value=value)
        sp.transfer(state_param, sp.mutez(0), merkle_aggregator_contract)

        sp.result(sp.record(registry=registry.value))


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
                registry=Type.Registry,
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
            action_number=self.data.outgoing_counter,
            merkle_aggregator=self.data.config.merkle_aggregator,
            registry=self.data.registry,
            payload=args.payload,
        )
        result = sp.compute(action_lambda(lambda_argument))

        self.data.registry = result.registry

    @sp.entry_point(parameter_type=Type.FulfillArgument)
    def fulfill(self, args):
        # TODO: Handle fulfillment

        # Get target address
        target_address = self.data.registry.get(
            (args.requester, args.script), message=Error.JOB_UNKNOWN
        )

        # Pass fulfillment to target contract
        target_contract = sp.contract(sp.TBytes, target_address, "fulfill").open_some(
            Error.INVALID_CONTRACT
        )
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
