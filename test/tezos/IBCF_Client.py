import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator
from contracts.tezos.IBCF_Client import IBCF_Client

from contracts.tezos.utils.bytes import bytes_to_bits


@sp.add_test(name="IBCF_Client")
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
            latest_state_update=sp.big_map(),
        )
    )

    scenario += ibcf

    ibcf_client = IBCF_Client()
    ibcf_client.update_initial_storage(
        sp.record(
            eth_contract=sp.bytes("0x"),
            storage_slot=sp.bytes(
                "0x0000000000000000000000000000000000000000000000000000000000000000"
            ),
            ibcf_tezos_state=ibcf.address,
            ibcf_eth_validator=ibcf.address,
            counter=0,
        )
    )

    scenario += ibcf_client

    ibcf_client.ping().run(level=BLOCK_LEVEL_1, source=admin.address)

    scenario.verify(
        ibcf.data.merkle_history[BLOCK_LEVEL_1].root
        == sp.bytes(
            "0x01099dcbff4b5cfd9c353fd372eb04f6b2cb0dcfcb69c4e48d895130d0189e9b"
        )
    )

    # TODO: Test pong entrypoint
