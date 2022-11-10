import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator
from contracts.tezos.blueprints.IBCF_AssetTeleport import IBCF_AssetTeleport


@sp.add_test(name="Blueprint_bridge")
def test():
    scenario = sp.test_scenario()

    BLOCK_LEVEL_1 = 1
    admin = sp.test_account("admin")
    eth_alice_address = sp.bytes("0x" + "11" * 20)
    eth_bob_address = sp.bytes("0x" + "22" * 20)
    eth_carl_address = sp.bytes("0x" + "33" * 20)

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
            registry=sp.big_map(),
            minter_address=admin.address,
            merkle_aggregator=aggregator.address,
        )
    )
    scenario += teleport

    # The registry should be empty at the start
    scenario.verify(~teleport.data.registry.contains(eth_alice_address))

    teleport.teleport(eth_address=eth_alice_address, amount=10).run(
        sender=admin, level=BLOCK_LEVEL_1
    )
    teleport.teleport(eth_address=eth_bob_address, amount=10).run(
        sender=admin, level=BLOCK_LEVEL_1
    )
    teleport.teleport(eth_address=eth_carl_address, amount=2).run(
        sender=admin, level=BLOCK_LEVEL_1
    )

    scenario.verify(teleport.data.registry[eth_alice_address] == 1)
    scenario.verify(teleport.data.registry[eth_bob_address] == 1)
    scenario.verify(teleport.data.registry[eth_carl_address] == 1)

    proof = aggregator.get_proof(
        sp.record(
            owner=teleport.address,
            key=sp.bytes("0x11111111111111111111111111111111111111118101"),
            level=sp.none,
        )
    )
    scenario.show(proof)
    scenario.show(sp.pack(teleport.address))

    scenario.verify(
        aggregator.verify_proof(
            sp.record(
                level=BLOCK_LEVEL_1,
                proof=proof.proof,
                state=sp.record(
                    owner=sp.pack(teleport.address),
                    key=proof.key,
                    value=proof.value,
                ),
            )
        )
        == sp.unit
    )
