import smartpy as sp

import contracts.tezos.IBCF_Aggregator
from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, ENCODE, Error
from contracts.tezos.IBCF_Client import IBCF_Client

from contracts.tezos.utils.bytes import bytes_to_bits

contracts.tezos.IBCF_Aggregator.HASH_FUNCTION = sp.blake2b


@sp.add_test(name="IBCF")
def test():
    admin = sp.test_account("admin")

    BLOCK_LEVEL_1 = 1

    scenario = sp.test_scenario()
    ibcf = IBCF_Aggregator()
    ibcf.update_initial_storage(
        sp.record(
            config=sp.record(
                administrator=admin.address,
                signers=sp.set(),
                history_ttl=5,
                max_state_size=32,
                max_states=1000,
            ),
            bytes_to_bits=bytes_to_bits,
            merkle_history=sp.big_map(),
            merkle_history_indexes=[],
        )
    )

    scenario += ibcf

    ibcf_client = IBCF_Client()
    ibcf_client.update_initial_storage(
        sp.record(locked=sp.map({0: 0}), ibcf_address=ibcf.address)
    )

    scenario += ibcf_client

    ibcf_client.lock(sp.record(token_id=0, amount=100)).run(
        level=BLOCK_LEVEL_1, source=admin.address
    )

    scenario.verify(
        ibcf.data.merkle_history[BLOCK_LEVEL_1].root
        == sp.bytes(
            "0x9089f66e4428c41a5ec16631b921eade5bb82aa3953cff9f4e8f9c80b9124c9f"
        )
    )
