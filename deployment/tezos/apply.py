import time
import yaml
import sys
from pytezos import ContractInterface, PyTezosClient, michelson, pytezos as PyTezos
from pytezos.operation.result import OperationResult
from termcolor import colored

from configs import deployment
from deployment.tezos.scripts.insert_multiple_states import insert_multiple_states


def get_address(pytezos_admin_client, operation_hash):
    max_tries = 10
    while max_tries > 0:
        max_tries -= 1
        try:
            opg = pytezos_admin_client.shell.blocks[-10:].find_operation(operation_hash)
            originated_contracts = OperationResult.originated_contracts(opg)

            if len(originated_contracts) >= 1:
                return originated_contracts[0]

            time.sleep(1)
        except Exception:
            pass


def wait_applied(pytezos_admin_client: PyTezosClient, operation_hash):
    max_tries = 10
    while max_tries > 0:
        max_tries -= 1
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
            msg = f'== Originating "{action["name"]}"'
            print(colored(msg, "green", attrs=["bold"]))

            code = ContractInterface.from_file(action["code_path"])
            storage = {}

            if "storage" in action:
                using_file = action["storage"].endswith(".tz")
                if isinstance(action["storage"], str) and using_file:
                    code.storage_from_file(action["storage"])
                    storage = code.storage.decode(code.storage.to_michelson())
                else:
                    storage = action["storage"]
            else:
                storage = code.storage.dummy()

            if "overrides" in action:

                def merge(storage, overrides):
                    if type(overrides) is dict:
                        for key in overrides.keys():
                            storage[key] = merge(
                                storage[key] if key in storage else {}, overrides[key]
                            )
                    elif storage is not None:
                        storage = overrides

                    return storage

                storage = merge(storage, action["overrides"])

            operation_group = client.origination(
                script=code.script(initial_storage=storage)
            ).send(ttl=115)

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
                using_file = action["script"].endswith(".tz")
                if using_file:
                    print(client.contract(action["contract_address"]))
                else:
                    Scripts[action["script"]](client, action, wait_applied)
            else:
                if "micheline" in action:
                    f = open(action["micheline"], "r")
                    parser = michelson.parse.MichelsonParser()
                    micheline = parser.parse(f.read())
                    ##print(client.contract(action["contract_address"]).parameter(micheline))
                    op = (
                        client.contract(action["contract_address"])
                        .using(block_id="head")
                        .parameter(
                            entrypoint=action["entrypoint"],
                            micheline=micheline,
                        )
                    )
                else:
                    op = (
                        client.contract(action["contract_address"])
                        .using(block_id="head")
                        .parameter(
                            action["entrypoint"],
                            action["argument"] if "argument" in action else None,
                        )
                    )

                if "amount" in action:
                    op = op.with_amount(action["amount"])

                wait_applied(client, op.send(ttl=115).hash())

    return contract_address_map


pytezos_client = PyTezos.using(
    key=deployment["pytezos"]["private_key"],
    shell=deployment["pytezos"]["rpc_endpoint"],
)
deployment["known_addresses"] = {
    **(deployment["known_addresses"] or {}),
    "admin_address": pytezos_client.key.public_key_hash(),
}
results = run_actions(pytezos_client)

# Save deployment results
with open(sys.argv[1], "w") as file:
    outputs = yaml.dump(results, file)
