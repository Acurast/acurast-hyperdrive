import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, EMPTY_TREE
from contracts.tezos.IBCF_Eth_Validator import IBCF_Eth_Validator
from contracts.tezos.blueprints.IBCF_Bridge import IBCF_Bridge
from contracts.tezos.blueprints.Asset import Asset
from contracts.tezos.utils.utils import RLP

# There values can be generated with "scripts/validate_eth_proof.js"
ETH_BLOCK_NUMBER = 8006370
ETH_BLOCK_ROOT_STATE = sp.bytes(
    "0xcfb6f70a0571923cb25951db72086cc426f49cb16cde0ac7680489e56781915d"
)
ETH_BRIDGE_ADDRESS = sp.bytes("0x7651c6BE451a6E71f8e34A04b3101aD216deB9ac")
ETH_ACCOUNT_PROOF = sp.bytes(
    "0xf90c01f90211a023cd52e1dfb8fa8d6c6d78396f14f6891eec6efe81cbe21be9296f509d963680a07b004714ffda4fce995da337282b8fafc06a69bccbeade8f9ed7713f323fc1b5a0fa34135608efd47e430d002ae1c490c2dd34b52f718add246257ac8114bb09d0a0bf5abdfcd814ed2b3c19c148bbb2a90e4a00c491a3d0654af1574cb36403e893a0a11f1bf9dd81884af7809621a06bc6b4ab28e9fe7e2625141c61be3f04a971fca0a22fb2f2fd364f0383cede84c5ceb94c6f2b28007cbee67d99d66dbba31e4262a007e058afd2e2fd59089b0c2434f4178b27026315aca119223bf6bb5cbd7ac630a080e5b6f9168d720f43906b6ca5e9b9639493fcc1eda3f8c0b5dfab421231da6ca05530ea7ac82754491450abdab569e8cb0d0ec03788cf203c9914fb7ff575d098a0cc8df47bb01e95862c98714912a14616f0490f8b3d2a47789cf7bfa01cdbc588a081fd045fc64e96ef3fd2fc397c831afef6c51ede07a6acb7289f60ad3efae760a0a78f24f209257337c79bf2df1c8e3ace748cf39264ac557ac10bf8ec1af7ae3ca053a94fbe23133396267980ac31b5617cec04b26af5884e63758743663b558a8ba082c91e2901ee2ce9b42bef1e845a6352f896496acab4ffa3c293b3218fa2325aa0325fbd0e1d7c0acf3aea401ab145e07e6086175b019d35bf678db293d2ca0428a0e71fbb06b5e069a853e26390b49f22c9bb6def177e6238b71ff86be99651fa7c80f90211a014e236f08700b0b8541f82784cd3902a25c8a847a8ea10442469074202cfca31a0708d2f8147607e36ad51e5a5e4ac03f917889a960e3631f3b8da78e2e95f8b9fa008fccf01d900558778f2d86c6b527ce4749c49414a5c2301cc08f3e31a8c0895a009fcc817ce11f11335c088af598e82cfdc40dd8ac59148923043e0869107d046a019735be6db279a72dbaefb79e8feefb06451e69158f4e7b0f810f3c64a86112da0a2ceaf83ebdbfe046d5e4300c2037ecc0b3fab0b2d363e4ebf66e082d2c5a41ca0444c0a80d14241633ab7cdf43afb7977f454cc4aee7cbfa8b873a3339677b0f2a0001015c0e2968883e191fa9323a44e3a7305fe455bb9a96dc566c41f665f1409a0c300592cd825758dbeb24f63e8acbc66d0f1ada85d356a4e5b9f79a06812d105a0052b4e44d46fed3a6e6bbadb13c76b19537af2a65b3090920312cce57f0ab62ba09f1bf46c4f1afe5d895f7fd521522045737ea5687e8e70454a0d3b432502be42a062149314263f43a2062b48debb82c2fb8e15a2e12f7dff8c8393bf9dd7bf98e6a0fdaaa6ceb0ee2eecb9a4ee9a4b20fc2769029149b4ac28c89f0d0f9da2e1a142a090322ad072749d9e60872a0d6b30a3312d0d7faa8d260feb5b7988de8420ba79a094c3f51492ab557e941860719abb414e11c1e2f53f1847217ca4f270d6e14968a0cf1bcedac0f091a1852e40042d4239c2746bfb668a5eeb21c5041d289925ecd380f90211a0dd5c70f03458b27dae9a97c89b56d380fcb4201676948332b5a62a5f51f57e29a0dcf69b1b464d01d0ed19ac87f3aae9af02ab82300e08a9430d5e9ffd9dbb88efa0eedf1a37275b946471ed13b62756907404964c66cab0297c94052ac5148dbd3ea00dc1903e2a8a99c38f93f5c7a1f4bf201b65e70632a293b657ea402ded0829aca0bcbc840251f401314c636447f01dc66e9ec3e32941aa2988694285a0519449d1a09360f86ce5a345980dc8d45c9075b46e37ff3adb3a79860e7cefe259841c9732a006aacb825c98fe5d998253e1dffa3204aa39c4eed91419642e16e8f1aa9f8941a024b1359ba60f3a919932fa3e14b06930c3d732a7422cc60ef5ba390b41f560bda0ef1b773f6d51d187fc980123b60833755e330bce95911a788fe169969db82657a063bf6cc2655a7cdc29cf95199f7b8b96516a9570c613473a75563d0c8002e0e7a0715b4b1b59f15d3523222c71f66cd5382d6abb090a12a49b09c9db1c5b4f2621a032c11437c5543eb0cdfa4f2e3d58f8ee8c79f73d18fbf1a51a3fa9cc3a915472a059901ad1daaf39b309cc472c1acb44ec0327d12f760223627a27b521db2863a5a0f065a37725209572ddb421cac58daec93da09291af6b6b14d0bc07a2ff79709aa0b2a79ec5bdfb34c536a24b27f6b27c6ceaae5b3329c51bbb81c76d4dcb3cedeba044d7730e43b12ffe81503846bf114c8d54e5ee2f125e31edb2059f028f43199b80f90211a087f7e76388b5c3697da874e0d8a39973940366656f7770757f7821a53324364aa04d2daea4c3ca387aa256c9045d83a92fb4a514c65622f39a6f07b57311d106b5a09512e331746ed44076f0d5bcf3e6dff813172f594d5d5d3ea71a1621025006b8a0126b1cf9796ed06ca9f453ee0922b21f15942b01137b532e23f78ebd58d54a8ca03f1c17d8a2f20978d36a805f001c0d76ef9c5d99390a03a8206a457a496679d6a0dcd54864a87fc02b5535091a8ccf30002a4d7c048d597d62203875f04f6b0504a0e80009e9b73cbaf615f79d7e29e17abec09b28fab836e3903f2ac2bc706f7518a041198580f88a1b232402819e7b17b363392b3a1cb2f664c0fa530087e5abafafa0047e1f15660b2539e28249d3abed07baae1ee1c5568187737196c3927a295154a0bb6ed24415924f11f3cefbfe591c01d7063bb5fa2c0b0a7f549b6b719e87cca1a08ad45390285d8225aa3ac7b5fc947bcf1a8be01320473aa841d019d63101c831a0af30b7eddecfce54bb554bffa462e184743127c077a3c6e2e4abf44099b1e365a09ff36510a7f714a0f4d5ba25f6710bac967f4228074bceda147c44978386f2ada05b650ef9c33e41cd321927ed3e4a17e918cca82ea688656fd597bbd696a63529a0308e42d2dcb0c09bf6cd3c665981fe9720a7f93ce9b01b9785b7ae4c6cdf06e8a0500b6d22d00e5e4983cfd5a86c58e10a0e0770ce5139a0c9194af7f827a8a1bb80f90211a061c016faad3041818125673cdf0cdb6369d27ba4db915238d96b68b4f66bbf51a03ecd7797bd004734ca01d7a5522d34b76f6ccc31563fccb6fe6faaddf04e12c4a030dbf114b664185e456b4cf0fbaea72f9b6d6977fc0492db89eef037a8ee2b2fa0078bfd0e52c16a48b7db5761b1aff9b739450509bbfa7b2dc656de7b36dcf61ba0402644da52bc198ad3f56a4076eec66550bb9f06eeaf875902996bc0db75334ba01bd66157009dafd0ef395c68b64db23860baaa7b68543ad1b785d8883c8f99c9a015d581bb90b779db0b99fc05e149c1ee4f503052b66c5980d697a52a853df10ea0f6a51e0b7058c0056f5ddb3caf0bc05448d7ed315e0997373d480549a8d91714a06c9541e55f0ca669fca5a9e3ef0a9e3b7e29076fe1a6591d381cdb5100551e34a0e8b988f1a68e0392789c94a8253784c524c22dafc2096d268f0c03feb01d6813a01803c8c380985b4659294fdd518430b5edb07d7f05ae916918f066a962b103f0a08f8604e6a89695368d697e874028352fcc68007ede7f1badd143a082ca58ace3a0e0dcbe23857388becd2d283099759333a3a5822db3a080eed759f21c95a73778a0cabdf09b191b2bff48f02a0055aa88fb8eb4c23b92561f4f2783f75f3db89cfea04b323f9ee64075a440d6e0ac2c46b83ee71361720e16c3bd9491d3c68dfd40dfa0f8a366a63cb3255d2d94a0d9ddf6366a473ad0c3eb0b5782874603d8903ab9b680f90131a02a8aa4c6f50674820831b249de232f63434d967ebd796126b141f55d7f7f173780a02e7139257ac9686ed07d1ac6742d9b07c9db4f68f205fa5d91ed7dc22c9d7b048080a0304009fd0a5fa19247fc30936436dd1ee0e63f5f90e081ac635015ec1071aed180a09d0988ab591523bc70cb36ce749cbced8240cabc219a52ce9bede3ea8895541ba04ba910db2ef0fdd0045bbfaa477bbdb9ac396596b2f6609880419290f8e86f7ba07668b2e6e943bdda7a70986d843449b708683ca697cd2009e8b78f996b4323f3a0756dd32713dd1d273cb9d940db5354630cb17d963376764f0e2aee5693a141f9a0c6a041e3d57542ea762ec333f1d723b5ac65b26b220632f5ab29a2baad7f427a8080a0ce178949c1f4358a59fef8ff712cf154650d4be9e8f19627c7399da4555349798080f8679e20fe6fb46b66d07053b9928bc269084eb22a5863200193c0984f80e4fa1ab846f8440180a0f27a58b6c50bb910c5c58d02de86c31f8189f844a0a00b236e47d40f770870dea02c3ac41a01db00a4e7d3f25693d737b2bc9cfb1a069b1681340ff60df29316e1"
)
ETH_DESTINATION_PROOF = sp.bytes(
    "0xf9016bf8d18080a0c505ed8b0a4735f2847db65c1de5a60d0878fc508e6a430e419cd24af6c7f0b18080a076d4d2679ffbcc738b3b9930474670daeaab3ccccbdd5baaa05fb991a78888d18080a0a682c80879d69b6f9c7371a587a3790057f945af3c10a694e0bfa386fa4362a68080a07a266775abbed2a2b0a635b2b07caac2b3ff8fb39d442f777f016c11d8f92e81a01f7e54f47fa32126cfaf069f1ecea7f7fb5f85b55fa0f5d23604e4915e2b5feb8080a0d7f5d37b844bfc68204a4edad936a63e32f51a2e21442c9a0118e270ed53084580f8518080a0566b2bc15f60eb8035f2c5e68382948ae65c5aefa0444a53827f34a797e012ae8080808080808080808080a0c59b14f003ace0c4184530d6bce4d5a6e4c54981792924bd38d26b3fa4272dc28080f843a02069ad09c79cd38934b567412ffa82bf024fcb938a8b7ec112fb038de5047bb2a1a0050a000000160000eaeec9ada5305ad61fc452a5ee9f7d4f55f8046700000038"
)
ETH_AMOUNT_PROOF = sp.bytes(
    "0xf8f6f8d18080a0c505ed8b0a4735f2847db65c1de5a60d0878fc508e6a430e419cd24af6c7f0b18080a076d4d2679ffbcc738b3b9930474670daeaab3ccccbdd5baaa05fb991a78888d18080a0a682c80879d69b6f9c7371a587a3790057f945af3c10a694e0bfa386fa4362a68080a07a266775abbed2a2b0a635b2b07caac2b3ff8fb39d442f777f016c11d8f92e81a01f7e54f47fa32126cfaf069f1ecea7f7fb5f85b55fa0f5d23604e4915e2b5feb8080a0d7f5d37b844bfc68204a4edad936a63e32f51a2e21442c9a0118e270ed53084580e2a036c9906f00400cd8011256368849abf5d045cb493cf4841c92ea0271eae73bbd0a"
)


def get_nonce(n):
    return sp.bytes("0x{:0>64}".format(hex(n)[2:]))


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

    scenario.show(alice.address)

    aggregator = IBCF_Aggregator()
    aggregator.update_initial_storage(
        sp.record(
            config=sp.record(
                administrator=admin.address, max_state_size=32, snapshot_duration=5
            ),
            snapshot_start_level=0,
            snapshot_counter=0,
            snapshot_level=sp.big_map(),
            merkle_tree=EMPTY_TREE,
        )
    )
    scenario += aggregator

    validator = IBCF_Eth_Validator()
    validator.update_initial_storage(
        config=sp.record(
            administrator=admin.address,
            validators=sp.set([alice.address, bob.address, claus.address]),
            minimum_endorsements=2,
            history_length=5,
            snapshot_interval=5,
        ),
        current_snapshot=0,
        state_root=sp.big_map(),
        history=sp.set(),
    )
    scenario += validator

    asset = Asset(metadata=sp.big_map(), administrator=admin.address)
    scenario += asset

    bridge = IBCF_Bridge()
    bridge.update_initial_storage(
        sp.record(
            nonce=0,
            wrap_nonce=sp.big_map(),
            registry=sp.big_map(),
            merkle_aggregator=aggregator.address,
            proof_validator=validator.address,
            asset_address=asset.address,
            eth_bridge_address=ETH_BRIDGE_ADDRESS,
        )
    )
    scenario += bridge

    asset.set_administrator(bridge.address).run(sender=admin)

    # Submit account proof for a given block (validator: alice)
    validator.submit_block_state_root(
        block_number=ETH_BLOCK_NUMBER,
        state_root=ETH_BLOCK_ROOT_STATE,
    ).run(sender=alice.address)

    # Submit account proof for a given block (validator: bob)
    validator.submit_block_state_root(
        block_number=ETH_BLOCK_NUMBER,
        state_root=ETH_BLOCK_ROOT_STATE,
    ).run(sender=bob.address)

    bridge.wrap(
        sp.record(
            block_number=ETH_BLOCK_NUMBER,
            nonce=get_nonce(2),
            account_proof_rlp=ETH_ACCOUNT_PROOF,
            destination_proof_rlp=ETH_DESTINATION_PROOF,
            amount_proof_rlp=ETH_AMOUNT_PROOF,
        )
    )

    # The registry should be empty at the start
    scenario.verify(~bridge.data.registry.contains(1))

    # Teleport tokens back to Ethereum (Expected to fail, bridge does not have permission to burn the tokens)
    bridge.unwrap(destination=eth_alice_address, amount=10).run(
        sender=alice.address,
        level=BLOCK_LEVEL_1,
        valid=False,
        exception="FA2_NOT_OPERATOR",
    )

    # Permit the bridge to burn tokens on your behalf.
    asset.update_operators(
        [
            sp.variant(
                "add_operator",
                sp.record(owner=alice.address, operator=bridge.address, token_id=0),
            )
        ]
    ).run(sender=alice.address)

    # Teleport tokens back to Ethereum
    bridge.unwrap(destination=eth_alice_address, amount=9).run(
        sender=alice.address, level=BLOCK_LEVEL_1
    )

    # Teleport tokens back to Ethereum (Expected to fail, not enough balance)
    bridge.unwrap(destination=eth_bob_address, amount=2).run(
        sender=alice.address,
        level=BLOCK_LEVEL_1,
        valid=False,
        exception="FA2_INSUFFICIENT_BALANCE",
    )

    # Teleport tokens back to Ethereum (Expected to fail, not enough balance)
    bridge.unwrap(destination=eth_bob_address, amount=1).run(
        sender=alice.address, level=BLOCK_LEVEL_1
    )

    scenario.verify(bridge.data.registry.contains(1))
    scenario.verify(bridge.data.registry.contains(2))

    # Validate unwrap proof

    rlp_nonce = RLP.Lambda.encode_nat()(1)

    proof = aggregator.get_proof(sp.record(owner=bridge.address, key=rlp_nonce))
    scenario.show(proof)

    scenario.verify(
        aggregator.verify_proof(
            sp.record(
                path=proof.path,
                state=sp.record(
                    owner=bridge.address,
                    key=proof.key,
                    value=proof.value,
                ),
            )
        )
        == sp.unit
    )
