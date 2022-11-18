import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator
from contracts.tezos.IBCF_Eth_Validator import IBCF_Eth_Validator
from contracts.tezos.blueprints.IBCF_Bridge import IBCF_Bridge
from contracts.tezos.blueprints.Asset import Asset
import contracts.tezos.utils.rlp as RLP

# There values can be generated with "scripts/validate_eth_proof.js"
ETH_BLOCK_NUMBER=7976909
ETH_BLOCK_ROOT_STATE=sp.bytes("0x36b3dce338be1121eb455b26f8298556e9008987d67811d287771e06de2f4e14")
ETH_BRIDGE_ADDRESS=sp.bytes("0x0C2dBba45E207619B79Fd7946496fbEc1E66fA8C")
ETH_ACCOUNT_PROOF = sp.bytes("0xf90c93f90211a0c994141a455887c56cd7a8a6144aa6b6ef6f106c4ee3f4b13a3fcffe232e1b5aa012cdfe643130c3a240192e749ec7ac37fe3eca043af2eb9c3d0e7c41183bf0e6a017a48ec11f654acb74f214bf7e078e58f28c86fc42061eaaa27c6c23d8d6a748a0910714794757f81fe869bedeed98c26000c0df6bdd80215d394116ec6f39448fa0088153fe056f6972565574dc6ecb96acdad08865c84f09b80d4c4ad67c58b0d5a07a4b12174d99fd9fbcb118be463951a0d2f23f062074e2b3495783d691240b90a07cee2a673d0a4d31732e958ba290c8832934aa2f42d93d5f130be084569771f6a0c9426aa1b9d9223107a678e4d2d89e2e2931be02268b967d301cc185d7b7822da045f5ea4b9a2679df20a5013aceeb3525e877ec9a3c27539b37b84d58621d24a6a0b498a183d99e2429bd3f5ef72e02cd98d96b55ee150fcf63e403022f5e04f639a0c571bb52fdda05012b9b29142d848d76038bdc884ff521e824f450cce87b178fa078304a94d6e2b35e952e961815e022b3d24bd1c8d7c90f2fca867b0216300e73a0263ac89aca8f812c22c91b20d8d3f3504733353f32693d8895e224b1557a0882a08b8fb08743d8780fa81184fc8f19711190cecccbe370ea85abbdab3a964b9d28a04590be53401d61824b8b367925ac641ec3acba883a2be8d7e831a39a27f3a2a5a0ba3d3f50ff3cfc455491660a94fe34c431aa3192a1632a768086476d260df02c80f90211a0cf1351aa7ea3b32d7ea1f577418ee0575e6ee96bb196ca41310d170f4884ef21a017979cdf414b3bb28bf9eb6de9bff33484cbe4c8e4f0dea861c6ea8b92553ef2a012252b7506722f72edd93784cd01e13006258747dddcb5768a8dd6dac516543aa07602332c27eb1c003fafbb280a9e1508c0cb29674bbb065fd525d1413233cd5fa019b1d8714f00d48849bbdd4db83f1a95576f3e56825b3c36cea53c9b26a94812a004847761c0778d9f0c178f62a3fb1e74fb344f599d5d06d9eacbb7fd9bae2bf3a0187e3870e8421ef2c6608df9836a1ee24e406a4f9a60b8e76399556232d36443a03b9a62567f669b35f9605b10603a60dc56671fb0907134d2c43cae1b9cef70a4a08ffd470b9a93bc31d0a48206d642091505803ca42e39774029d5c90d68b81332a01c2b2b5a02e98d465c72951dbf8a17cb9b124da5d15af720a218ed467bdedbc6a0de827db3281fab20dbb3db20b6245a4238284e46bc35727bf17e10b8c064087ea0c520639671894cb49d5d5e2a452156ecb1eb5f662c4c5e0353227ddb3edbdfafa0720b64856c92f21aff53b9f11202fb214cef84396aba1ba2c6958dc6a009f8eba0109079f150f182055e6991ebaaeb30985033331ba7a931d449ef7558fb1b7d93a0f48cf83e404a64d79d85d6cba118ddd638965d0963d6a8c28236961322522c4ba044847bedeed802f4cc48dd9f05069c39d9d86df0c42c3d92ab48262d65229d4680f90211a0877e9f3bc1a531a676097ec1ce778b7c833ab8403e7e0108b489feba1851494ea0ff532c30ab95003944b65dbf845c0b6455036cddcb7eb73b0013cc927bfc862da0cdb23a8aea6c7af7de63346d51fb42c3e04c4830cd1f8cb37fa037072e14e538a0b77b5bf3cf97a3972ce870f407a2a14ff5a550154834765558a76dc2e2e1cf6ea0f502f5fc2d09a26767d01675e294aaa4b2a426ff20b0a7e0c2f0cc9e10d245f8a0420af5a9fed7c34d4dd7611ad1c059202ee19a1f1b413950bd1ac8981944b739a0348ae7701eb424235a188447a9b04195b445b3081584bec83bb7d8519b79ec6da06a93ea69680d645b6875ade1ac1fcd3bb3a50196909ab900280a89ccf9ebcd79a0f7230f058d02beb7a95545f123beb6fdd9a370035d7331b653f4e4aa4398cb57a0dd42c2cc0a4e9232dd00137ddb1d9a40572613edf0a8a20d15b60b69c00345bfa06a47cfa1b11637dd5b5f2eb88605360fefeeab3a405c7000a2c0af0dff58f8cda07170c08a67e18f36bf1c206db2e39880ded8a2b02c0896ea3b4d04e68db084dea00910bad5a60007b8de73bd373ba3f3aa287cdc96b442486f56cbdd3f39a945e4a0b790d37fc8f44ca6b63486dafcaf30a9333187d42f1d994d0be8e7747c469a80a02fb8d53429028ef61f82c9881b0513da3a9f953bb3fedd224f0e2d82487fbffca01ab9a8dc8f3fb5cf27e01f96166e5933032312e89fcd1cbfa09d6cf5591577ae80f90211a0e23f3c353d0d0ce2ae5a8fd9f31a6e62dfd2413b4ef41694fe00cec8e3fa6ab5a0c55f6e009a9cbb937887e39a7da8c3adbbd69d3977351b815bebe2d76e54975aa048eef15a24496109785fd26870ba97dc32e6957580425daeebc91dc867fd77f1a0a9577ef7310ab181b89dd8d5534445d3a50f29b8a381b4811b235021d6ab22e3a0fdf6b53874c9051440b658f4ab16678f896ebf105280c20ff32847e956642510a0e0edd8d6619a679ff6b7c51b7141d4fb3abdc45f7a0d4667196bbce09a127abea0b49d11963a2c5e1a3a58553772642879674c6076ee5caf040817b1f727303a16a03befa938a290fa88b87adcbf5c8d185a489c060af7ff73d96771a960f40bc8cfa0fff12af1097368e79e3e112432edc8c4a53152abc604858aa38d3271b38388daa0587f11e40ab561446dec585842b84a5f777b7194dac39e5b12556641f6d41b41a0e53c4b55e28f6ed6605ff6f72cc05c8eb4e78c7e93051ac3976c68f7fc82c3efa080e09db8c7d1d829dd80d3facd7f3d6de639aafe71b93e9216624fc62eb71267a05bb9337744a3a1c446a164c33f6ead3d8ce539208f8090aa1c6900117645b313a0776c3cc32212ce3e07f148ff26607cf244cc5663bdd6e2a55a1cf45facc4ba0fa08a332ec3378b6f75962522f19b47db9529e87c595f493edbabcc9133e8b330f3a00f0bf24e535e8a15d7c4f1687d817be5cc9c3eb3177aebe2f66715942f619e9880f90211a000d5f1599064414d8f619f48ed3e05725be6096903a9f5ac61a436d1aa2ad1b1a0a72ded5dff8763cdc9343385267ac61e9ec51818b49964b3de0ed72616c6e6c7a0c8ba8da9cf4a35048569fbf08e0199c9f0d96ef23b3752058e2b7ca5f1b6cab8a05c658b74ebee43d47d8e0a9640a44199d4bb1b32ef6d1975c4517ad601ab6d71a04141aa1b6879fc1e2886e608060b9c795d5981982b3a2a7be6cf1d5985236cf8a0cd9a1ccc379a3b47c3e6a8ac14b1237db50f3ed64a5ea13e34b9bc4c949467bea09d6aadbf742461c731dd493de5201cd4b5fbb448d5e6e7f166876d504eba362fa0f73c97ce1b521d115aa525568d2b984ecce9ab24e60c41e44a086b472351b334a0e1b0ba54c9fd19ba2569d159718a561e24b4063f4251fe4301e26180e60d91c0a08bf0270caaf07d4a8f9b9b3de3b50f8760536eaac9f60cddb417e6d979a32b6da0373bd997a734b95402c9521ef544df09a6695b7eb8810f0faa6fab5ee91c05b8a052b94aada88328a9642f324fb474ce19e1c10a46ef9e0afb2665ea77bb0afc9ea0571d3ad7f1af2d5364b0fe3b2b90baff9d56b8a50804c7f862411df5654bf1f1a0cffd8120beac1bed71459fcb306b16d2799af1de59e1d2cf0d01f7103acbe7e0a056ec8a174ee68d6f352b62f53bf84ef3e270c824dd31c20d5858bbfbd4ba5221a059d1132f889b2b9e8aae432ccbb3d227b7a5083f64a4a0935b7f952b8228555780f90151a0365fcd8e0e250d7c217c2fc757eb98b044871f0198071f18f8bb2c3332f454018080a09310501b8b83bbd947f59ce4ce28788ec154a4d382e47e05c31d810b0a70664f80a0a6f11c97ff652beac17b77340b884c1dee834da4c9b92fde489ae601c2c13389a01197b50829bb3993652eb412e6d183010b894b07f92b206a2243f0b9089b1029a060e3e6316a7af66558dfc143884c2cdf335a2c06a8d96a848b0688650a18df71a0222d7a4fdc2356731c80f045ba0596a246133030042aba1778b30fa2b8ab545e808080a0730c0309ac96f782e76de621bd1ca8c3a4987929021dc3c1d5f178fea83e0695a057a78c57f2635b72d0d40465a2fa9f39b06ac5a4ffcb92ddaad7636830ed3e6ea0fcf2db8a9f87832a554b8e5396cadf3daf0d4e27401728504c98f07521148897a03c9fd4329f1cb03df53e783939c65105668ac4b0780df83f8d6094d0a9ee9cea80f87180808080a0b5d3e2d346dff908dd7f55b55022d520cc755bbd8aff6c343502de961308758480a090ce600462420e24938bdca204370ebf9362d7493673de87f82b19727a2dedd880808080808080a0ffa166982db8e87ed8a7c25e414aea63a4b4f8382d63af6ceba8897ea3ffbc208080f8669d3703ac421568a881e65711ba3ac4203a90825e99cbf6cbe6eb26a1c079b846f8440180a097443f427a96ac3c3c56eb9034c9cc4b40b0d35dd31b31136e6fac2d7c9fb46ea0f5ccdc4cd711a264b90ea49e86e0a48bcc2470335ae0de18bd6c8fca7c74d1ef")
ETH_STORAGE_PROOF = sp.bytes("0xf8d6f8b1a00f76d95a267a39f8ed7b76d9ecae4f31e38cfde06e493a88fb29d8c8583abb7b80a02dbe82dbab23c0f57a617d29d657983defca5a1b696cd3378236c4bc065b73b780a033ae56dea38ea74e3b8c1c8e18f897361894d3154c59d3392cbdb835356188f180a0fea24806460c5abc118ba796dd6635f36ffd5bc9ebfec06dd5abaf60657b326b80808080a0348f4eacca66134c6548ef8091efdd539fece11911be6d98b94b4f78acecb16b8080808080e2a03afbbe886b7fa5695238505a40f969b45b7d3103f24a01a6a7e0475c4f432c180a")

@sp.add_test(name="IBCF_Bridge")
def test():
    scenario = sp.test_scenario()

    BLOCK_LEVEL_1 = 1
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    claus = sp.test_account("claus")
    eth_alice_address = sp.bytes("0x" + "11" * 20)
    eth_bob_address = sp.bytes("0x" + "22" * 20)

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

    validator = IBCF_Eth_Validator()
    validator.update_initial_storage(
        config=sp.record(
            administrator=admin.address,
            validators=sp.set([alice.address, bob.address, claus.address]),
            minimum_endorsements=2,
        ),
        block_state_root=sp.big_map(),
    )
    scenario += validator

    asset = Asset(
        metadata = sp.big_map(),
        administrator = admin.address
    )
    scenario += asset

    bridge = IBCF_Bridge()
    bridge.update_initial_storage(
        sp.record(
            registry=sp.big_map(),
            ethereum_nonce = sp.big_map(),
            merkle_aggregator   = aggregator.address,
            proof_validator     = validator.address,
            asset_address       = asset.address,
            eth_bridge_address  = ETH_BRIDGE_ADDRESS,
        )
    )
    scenario += bridge

    asset.set_administrator(bridge.address).run(sender=admin)

    # Submit account proof for a given block (validator: alice)
    validator.submit_block_state_root(
        block_number = ETH_BLOCK_NUMBER,
        state_root = ETH_BLOCK_ROOT_STATE,
    ).run(sender=alice.address)

    # Submit account proof for a given block (validator: bob)
    validator.submit_block_state_root(
        block_number = ETH_BLOCK_NUMBER,
        state_root = ETH_BLOCK_ROOT_STATE,
    ).run(sender=bob.address)

    bridge.wrap(
        sp.record(
            block_number = ETH_BLOCK_NUMBER,
            account_proof_rlp = ETH_ACCOUNT_PROOF,
            storage_proof_rlp = ETH_STORAGE_PROOF,
            destination = alice.address
        )
    )

    # The registry should be empty at the start
    scenario.verify(~bridge.data.registry.contains(eth_alice_address))

    # Teleport tokens back to Ethereum (Expected to fail, bridge does not have permission to burn the tokens)
    bridge.unwrap(eth_address=eth_alice_address, amount=10).run(
        sender=alice.address, level=BLOCK_LEVEL_1, valid=False, exception="FA2_NOT_OPERATOR")

    # Permit the bridge to burn tokens on your behalf.
    asset.update_operators(
        [sp.variant("add_operator", sp.record(owner=alice.address, operator=bridge.address, token_id=0))]
    ).run(sender=alice.address)

    # Teleport tokens back to Ethereum
    bridge.unwrap(eth_address=eth_alice_address, amount=9).run(
        sender=alice.address, level=BLOCK_LEVEL_1
    )

    # Teleport tokens back to Ethereum (Expected to fail, not enough balance)
    bridge.unwrap(eth_address=eth_bob_address, amount=2).run(
        sender=alice.address, level=BLOCK_LEVEL_1, valid=False, exception="FA2_INSUFFICIENT_BALANCE")

    # Teleport tokens back to Ethereum (Expected to fail, not enough balance)
    bridge.unwrap(eth_address=eth_bob_address, amount=1).run(
        sender=alice.address, level=BLOCK_LEVEL_1
    )

    scenario.verify(bridge.data.registry[eth_alice_address] == 1)
    scenario.verify(bridge.data.registry[eth_bob_address] == 1)

    # Validate teleport proof

    rlp_eth_address = RLP.Lambda.with_length_prefix(eth_alice_address)
    rlp_counter = RLP.Lambda.encode_nat(1)
    key = RLP.Lambda.encode_list([rlp_eth_address, rlp_counter])

    proof = aggregator.get_proof(
        sp.record(
            owner   = bridge.address,
            key     = key,
            level   = sp.none,
        )
    )
    scenario.show(proof)

    scenario.verify(
        aggregator.verify_proof(
            sp.record(
                level=BLOCK_LEVEL_1,
                proof=proof.proof,
                state=sp.record(
                    owner=sp.pack(bridge.address),
                    key=proof.key,
                    value=proof.value,
                ),
            )
        )
        == sp.unit
    )
