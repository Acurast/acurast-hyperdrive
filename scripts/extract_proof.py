import sys
from pprint import pprint
from pytezos import pytezos


OWNER = "KT1AJmMPMdy5D9P6CW33VWNGSkiVJc7CRFVr"
KEY = "counter".encode("utf-8").hex()
LEVEL = 967341

client = pytezos.using(shell=sys.argv[1])

contract = client.contract(sys.argv[2])

proof = contract.get_proof({"owner": OWNER, "key": KEY, "level": LEVEL}).onchain_view()

proof["merkle_root"] = "0x" + proof["merkle_root"].hex()

for item, _ in enumerate(proof["proof"]):
    if "Left" in proof["proof"][item]:
        proof["proof"][item] = [
            "0x" + proof["proof"][item]["Left"].hex(),
            "0x" + "0" * 64,
        ]
    else:
        proof["proof"][item] = [
            "0x" + "0" * 64,
            "0x" + proof["proof"][item]["Right"].hex(),
        ]

pprint(proof)
