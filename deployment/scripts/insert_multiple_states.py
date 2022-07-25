from pytezos import PyTezosClient

TOTAL_INSERTS = 3000
OPS_PER_BLOCK = 5


def insert_multiple_states(client: PyTezosClient, action: dict, wait_applied):
    contract = client.contract(action["contract_address"])
    for i in range(0, TOTAL_INSERTS // OPS_PER_BLOCK):
        ops = []
        for j in range(i * OPS_PER_BLOCK, (i + 1) * OPS_PER_BLOCK):
            key = int(j).to_bytes(32, "big").hex()
            value = int(j).to_bytes(32, "big").hex()

            ops.append(
                contract.parameter(action["entrypoint"], {"key": key, "value": value})
            )

        print("Sending batch:", i + 1)
        while True:
            try:
                wait_applied(client, client.bulk(*ops).send(ttl=115).hash())
                break
            except Exception as ex:
                print("Failed:", ex)
                print("Retrying batch:", i + 1)
                continue
