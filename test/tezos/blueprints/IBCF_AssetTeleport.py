import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator
from contracts.tezos.blueprints.IBCF_AssetTeleport import IBCF_AssetTeleport

@sp.add_test(name="Blueprint_bridge")
def test():
    scenario = sp.test_scenario()

    admin = sp.test_account("admin")
    eth_address = sp.bytes("0x0001")

    aggregator = IBCF_Aggregator()
    aggregator.update_initial_storage(
        sp.record(
            config=sp.record(
                administrator=admin.address,
                signers=sp.set(),
                history_ttl=5,
                max_state_size=32,
                max_states=1000,
            ),
            merkle_history=sp.big_map(),
            merkle_history_indexes=[],
            latest_state_update=sp.big_map(),
        )
    )
    scenario += aggregator

    teleport = IBCF_AssetTeleport()
    teleport.update_initial_storage(
        sp.record(
            registry = sp.big_map(),
            minter_address = admin.address,
            merkle_aggregator = aggregator.address
        )
    )
    scenario += teleport

    scenario.verify(~teleport.data.registry.contains(eth_address))

    teleport.teleport(eth_address = eth_address, amount = 10).run(sender=admin)

    scenario.verify(teleport.data.registry[eth_address] == 1)
