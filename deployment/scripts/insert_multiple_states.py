from pytezos import PyTezosClient

TOTAL_INSERTS = 1000
OPS_PER_BLOCK = 5


def insert_multiple_states(client: PyTezosClient, action: dict):
    contract = client.contract(action["contract_address"])
    for i in range(0, TOTAL_INSERTS // OPS_PER_BLOCK):
        ops = []
        for j in range(i * OPS_PER_BLOCK, (i + 1) * OPS_PER_BLOCK):
            key = int(j).to_bytes(15, "big").hex()
            value = int(j).to_bytes(15, "big").hex()

            ops.append(
                contract.parameter(action["entrypoint"], {"key": key, "value": value})
            )

        print("Sent batch:", i + 1)
        while True:
            try:
                client.bulk(*ops).send(min_confirmations=1)
                break
            except Exception:
                continue
