import time
import yaml
import sys
from pytezos import ContractInterface, PyTezosClient, pytezos
from pytezos.operation.result import OperationResult
from termcolor import colored

from configs import deployment
from deployment.scripts.insert_multiple_states import insert_multiple_states

def get_address(pytezos_admin_client, operation_hash):
    while True:
        try:
            opg = pytezos_admin_client.shell.blocks[-10:].find_operation(operation_hash)
            originated_contracts = OperationResult.originated_contracts(opg)

            if len(originated_contracts) >= 1:
                return originated_contracts[0]

            time.sleep(1)
        except Exception:
            pass


def wait_applied(pytezos_admin_client: PyTezosClient, operation_hash):
    while True:
        try:
            opg = pytezos_admin_client.shell.blocks[-10:].find_operation(operation_hash)

            if OperationResult.is_applied(opg):
                return pytezos_admin_client.shell.head.level()

            time.sleep(1)
        except Exception:
            pass


class ActionKind:
    """
    Defines all deployment action types
    """

    origination = "origination"
    contract_call = "contract_call"


Scripts = {"insert_multiple_states": insert_multiple_states}


def run_actions(client: PyTezosClient):
    """
    Iterates over each deployment action and executes it
    """

    # Maps contract names to their addresses
    contract_address_map = {}

    def resolve_address(address: str) -> str:
        # Expand oracle address from previous deployments
        if address in contract_address_map:
            return contract_address_map[address]
        elif address in deployment["known_addresses"]:
            return deployment["known_addresses"][address]

        return address

    def resolve_addresses(config):
        if isinstance(config, list):
            for idx, item in enumerate(config):
                if isinstance(item, str):
                    config[idx] = resolve_address(item)
                else:
                    resolve_addresses(item)
        elif isinstance(config, dict):
            for key in config:
                if isinstance(config[key], str):
                    config[key] = resolve_address(config[key])
                else:
                    resolve_addresses(config[key])

    for action in deployment["actions"]:
        # Apply value expansions from previous deployments
        resolve_addresses(action)

        if action["kind"] == ActionKind.origination:
            print(
                colored(f'== Originating "{action["name"]}"', "green", attrs=["bold"])
            )

            code = ContractInterface.from_file(action["code_path"])
            storage = {}

            if isinstance(action["storage"], str):
                code.storage_from_file(action["storage"])
                storage = code.storage.decode(code.storage.to_michelson())
            else:
                storage = code.storage.dummy()

            if "overrides" in action:
                storage = {**storage, **action["overrides"]}

            operation_group = client.origination(
                script=code.script(initial_storage=storage)
            ).send(ttl = 120)

            wait_applied(client, operation_group.hash())

            contract_address_map[action["name"]] = get_address(
                client, operation_group.hash()
            )

            print(f'\tContract Address: {contract_address_map[action["name"]]}')

        elif action["kind"] == ActionKind.contract_call:
            if "disabled" in action and action["disabled"]:
                print(
                    colored(
                        f'Skip action: {action["description"]}', "red", attrs=["bold"]
                    )
                )
                continue

            print(
                colored(
                    f'== Calling contract "{action["contract_address"]}%{action["entrypoint"]}"',
                    "blue",
                    attrs=["bold"],
                )
            )
            if "description" in action:
                print(f'\t{action["description"]}')

            if "script" in action:
                Scripts[action["script"]](client, action, wait_applied)
            else:
                op = client.contract(action["contract_address"]).using(block_id="head").parameter(
                    action["entrypoint"], action["argument"]
                )

                if "amount" in action:
                    op = op.with_amount(action["amount"])

                wait_applied(client, op.send(ttl=120).hash())

    return contract_address_map


pytezos_client = pytezos.using(
    key=deployment["pytezos"]["private_key"],
    shell=deployment["pytezos"]["rpc_endpoint"],
)
deployment["known_addresses"]["admin_address"] = pytezos_client.key.public_key_hash()
results = run_actions(pytezos_client)

# Save deployment results
with open(sys.argv[1], "w") as file:
    outputs = yaml.dump(results, file)
