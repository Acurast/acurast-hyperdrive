import sys
from pprint import pprint
from pytezos import pytezos


OWNER = "tz1aBNXcSKfWE7aujp2Twa7V7Beua2fjhri3"
KEY = int(999).to_bytes(15, "big").hex()
LEVEL = 867292

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
