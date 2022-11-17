import smartpy as sp

from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator
from contracts.tezos.IBCF_Eth_Validator import IBCF_Eth_Validator
from contracts.tezos.blueprints.IBCF_Bridge import IBCF_Bridge
from contracts.tezos.blueprints.Asset import Asset
import contracts.tezos.utils.rlp as RLP

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

    scenario.show([alice.address])
    scenario.show(sp.pack(sp.address("tz1f2k9M3ztqtbCTk5EmEepboEJxksXvafaU")))
    scenario.show(sp.unpack(sp.pack(sp.address("tz1f2k9M3ztqtbCTk5EmEepboEJxksXvafaU")), sp.TAddress))

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
            eth_bridge_address  = sp.bytes("0x15862e73957701C56892D8C689A6189A16c8e05d"),
        )
    )
    scenario += bridge

    asset.set_administrator(bridge.address).run(sender=admin)

    # Submit account proof for a given block (validator: alice)
    validator.submit_block_state_root(
        block_number = 7934545,
        state_root = sp.bytes("0xe3ca8df196492e62a0554068a03a58d7d934b56003cbef8be79e756288e09cba"),
    ).run(sender=alice.address)

    # Submit account proof for a given block (validator: bob)
    validator.submit_block_state_root(
        block_number = 7934545,
        state_root = sp.bytes("0xe3ca8df196492e62a0554068a03a58d7d934b56003cbef8be79e756288e09cba"),
    ).run(sender=bob.address)

    bridge.receive_teleport(
        sp.record(
            block_number = 7934545,
            account_proof_rlp = sp.bytes("0xf90c93f90211a0cd5568e490ccf637baf81de35ed8381e578dbd9ec93925454b9ef52a157d7c53a0f77b7c02af9da031cd84b5774db24f586b5f50be39aa7b193e2103cb51862cf2a08e613b4a2f8ef214dd76627c0cfa908b2b314745381624972d4fdc28f941d5a0a0ad0871e1ee8670b2e46a0fb612380b945bad0709c9b7af83602ac0e0d6375653a07359d3307a2020c83262a1894d0143d8192263088abb8879f7d6e08840462af2a0678fb624b3970d75c7ec181e513d7f569730ba5d8e3c976a33c775d0fda1c4b2a05e25b9cbd2ac6b15c6b53fb8a5dfc3398efdb220d9baf5529ba0dcf9c0b83331a0a3f8fa48446eaa4755a3ec55fc6280fe3a45662a2faa32451170b95b93004cfea027e44ed6e3b9fb63021c06d2e817735115b4a695768ce055bf30d963e5c48804a09a464c64e52aa9f63ba25c46b59d1f40dd12d24fe56163f48ee7702e7c6531ada0c2cd5694e3069f9f34d90dd86906b893aa1ffe4956ab13c0b84a0d97a71c05cda015f0c7b4dba02a07aa1e1bd8e2f1dd35b15ba9359ee7f8c050e8f0e015c6e86ba02dc863911e35c3e176d895721577ab82f10ecb1b3f4db44c61dda65cc70bcc5aa0ed3bf07bb146b6edc4cdf5616a1e6807bbb3beb5a0262b6d69b30766a56794a0a0a2d7b81656bed026cbca8235f48f95742a2d2300a703cbb56985cf7a21e3ccb3a0a3d1c65206935b50ed0fcc3bad4ae064014b47b46dfed5dbc3edaf06d00f3c3980f90211a084a7936e40c68ddea9fe62ac57f29a976f88a20dbca75698e17eede4444bb7a5a0beec8f4edc44604730c92577cf151d8bf73f8d1ba944fae1ff39ec495b6676f4a01c3d3a27f234b99af767ce1b9c673ad799e922c7eba71c73487bbfa04f6ef176a03922f6a9dd5f280d5ce3cbc35d5997a37a167761665231bf990bd28aea8be2c2a0ad3e3ce7e67228e1bc302025bf13b13c31b6171c4cbb01dd5520d1988a7098d6a0bf178c13a712ca33b5754d8fa6a2ebc417b1fae36ecab8b63d169c6e2f4f0ac8a0daaf8480eec51e66f40e17ac51d9befa5f8e6958ad8125ac6db6ed244687f66ba0097db180bf2eecbaec25b6011f492c90d17b7ebba00ac148391c6426ae033c68a0264d05b00b731d55a20c7fd0c737faa3fe1db3ae2d2428226ee7ea27650de198a026e50f798bcae532b3eded0968ee18c20d6c0e8759a9efaa078d74fbf04b2132a057cb71eeef74f17d32d2ce5e52f30ba50789be51c95024da576e8d3628a22beba04ab7e0dc8cb740809ce6bfc964354b50a666dd51223c110210bd1f1df8a41195a08273858c91f2cb23a8d7464a3e8e6cebf4f70e627bf0d9abc3a1fdb41debdf25a0225cbe626420631f11e2346cd04683ff05ca531f922d8cc01d1f58054f0a7dfca085571248cbb32a58e5da05489bacf745eae4deeb72c73b02c08d30e561e73292a042109ab37e52850628dc3c178839c40247c815aa81cc4854b6c680af8755d8fb80f90211a05471c6daf00262a91923c3ef062a4bce0acd27b6a3ef1e5bcd0444eac9789e4aa03618a302cfc6999b92c7123ba4d3ff6a4c1a623cb1222ba150457abddfbddc79a0cd0a8aef5c63890e36033b357b182b97d1a67653a04a9455faad2eed0a3cb32aa0e4ce13c98ad6b92dc15159dd4ba9a2d50365c2cde32b37ce676e0577da67c26ba0540a9c3af7ee145b54555cff19a4d0894b1892690c340a740fc7fa94722fe397a087668d5f62f3be151f1c3cd6a540a19baa4cd616be121f5c274ca179f764e4b7a0c0837ed2b7aa5e1b9352fdea6f9e261fa03a4bd2aab1366181e312336e75796aa02d482a9c704b2d060a2c45c5b2be33d8d5edd4c52d9df40a70fac352a3b3d45fa02fe89ee4baf702a0f504fc83fdaf5d9a2f2893c9d61eaeda3ccdf75daa547265a0a9151c36594b7523a61262d3db0213a43a38ea8450c5d1706fca859c0741fa4aa048dee53a008470f57e277b248df7cde3a4e11a93f6eb87c01c5eee3cf08440b1a018276ec4f99dfd59c8896adec214cbba75f2a70ca2c029e905f5a95ffe964c40a08fc1e3eb7c1febb5d73c3afae090c3c25a373a668076afb0bffeaa1e65ac70b0a0dabe6fafa1dab82c0a76bc3969d3e76ec4f2e8cae4502c59bd7c555cabe19124a0d43e5012e50a3b90e77e6e395249eeb47da137450b0845ba811c766ca1ad1e56a02d257f294b00ece10882f2689aba6fc1001947663695447ac4ec8e51ced31dd080f90211a005830eb2f8c7c857a0c754a17bee06509fd1347f50ee688cb81642ddaa05cc23a058a832cbb5c97470db90f2e4d7acdb15a78dafa052587ae041b725f37f293849a05f57ddbd8628bab602a0723f9670169ad0bd8138e17c0898c320e661e548c58ba06de87eceea71e84e6477256855a1d36a6f208e33f60d3c62a30d1d7525005c22a003cbab95b168461e41aab718e4701dedd63df8186d5193013db29fcf7fb9bd96a0a81ca76c4843605341525789b24272c825e875689c5324214fff567e712326efa013c8fd1008d41a1f2414f94b9e702af57c86afdf2be77f487347057b304b9cc2a0128b1c3affbfc04fe88116f5e1d876979ab42e1555646601a5ec84d141dabcfba0749ffcdac8504a18d9d4801b768ae08dfa63b38931f691d3861e58ac1c110380a0927dd60acc854305b43c08ea7b934c1601293af07e4afbaad2c7120159fda1daa059f71d83b42b6a1ac94ea408ef9b4acd8e6a6a1aacf4315ba9da2bc3b1418f6fa07bd32a9e852f21de13104110f3f3d6820a52e77e0ec8a793d67d69448c61e912a0b19bad7d2ea48c86f12e810fe5046a59073a05365137e1c0b5decafd4086a5faa0acc5cb200b1a6cf854a4ae26798e9adb83cefca15caf238b0fe79c52998ee879a02111aa9a51219d0b4cff8c326e2d56ee82d7f8bd95e8bfdf1c54ec62614cf9bea07e9185853e2822d8f2be0940862f7d4b75d63c63b0d67c528fbaa8d17e579e2e80f90211a0d1494b0878e75774bc5dc596f3eb440187fcbb58070912b29711ccd03bb2b68ea0dea2765b6c695d98368a7e518646ba8fbfc4d5e122558635750b33a69edf858da0db6526b442b947dcb4c1f9f523eeeede0ed6e045dd8fb14c0ca41ca24714b7e6a030dcab42a8e8ec23d19a78544ef859301f3c378b07e56908443816603cfbe352a01f5b0e488d13a095233c19eea4e5492a41b6e889d097d9f99612fa6f630258e4a038c074b6b9f46b6cb7449302e52f292aefb4dae01fb32f81697ac2b1986e2183a0a142f36aa52aeda9a3d84e717afd1df306c52ee85a9f3cea2feef20212b83bdca0cd827213ccf917f1e0d4a328ec644fabeafd29fd179e2996b79a4d14d745ac20a046e1dca9075458997d912f552d46b517a396f4ea66cfc73f816957c4fa271920a01ad6b6d0ca5686eef5cb3632bf0a461092cdca838244276bb7a99f13b1b00f21a010e76dccf45fa781992b74cdfb5041cbd3a57202469fcfbef88fdca51b47d7f2a0306610cc4e1ee5e3aca519dd928266fc1028d2edf444c500af2871f24e4fa894a0c2915abe7cc965173824ade58ff1d6a6dbb3b75998d9af8162da5997a00a56cea03b778de841b20462a56feee22b05a32eac0274db9c347cf89ace47a16f2831eaa06a0088236f394951d494a186fd1b6e82964f4d7a2c4d8d574947c1f4ba5a2e45a0c54da4d9b8885dcc68a73cf69916df3b5743d01f303813f987bf777f226d3fa080f90171a0abae1eeac79556e0b2b4832b5f7f0b7b87fcebca360fee3a61111c9e410235e4a019a71b42559781e441a4978c73f756e32ed570cfafd13068f2508137db459bb5a0617c654cbb278a43d3fd207a8a4be2c36a35c99a885fcb15c5b09ad11c4062a0a0b751ef4374d6ace87aa59b602c60dc49b002e7d072429123ae49d46d174c36eca0e5d3eeec19a5b1cb63bdd35d0515c194d1b5868c7fa87b0a88478eb78f8348f9a08e6bd4ea6f98571ee6941900da3e2a6195d7b157f283557d7db6e483c2b9ccf780a05aff18c4053899a59add28a87a8019d0402c111099dc65848db24d8a17b20a80a0f8601b21ccbca6f43bddb68f7a206147af94ccb8ca4a7de2a6e1b06825b0f333a0a98d19315714ed4d6199d888c2beb51caf3e1f41342d0f50f797f8099f0f16b180a04d3851582068e3c2f4169484a4b6fc881a832b8dabd73d9a04afc6d3432cdceba00caaa194ddb7bb5111a500a9d84ae72d08439e47a263a2e05d870263e888b9c880808080f8518080808080a0e7d029cc762017e1bda02be280a8f27f61f85f46c92c2cb53d4d5e67ef31e0c28080808080a0b591b1812307b87a765718adab5d9e944f29e55861635402ebacddace0aebed68080808080f8669d3293c27d7ed205d98102b0de1a9ff73fa58095af23b45ba7051729329eb846f8440180a0b467407fc726f6f7c5f900a02f6630dd19a7820069a0b04384a2d758b2ddda4da01d125ddd88fb78bbc4a6bd213c1403614fc5a678ed0415aef65e082396698648"),
            storage_proof_rlp = sp.bytes("0xf8d6f8b1a0e6669aceca44e35062d617399056d56fa52b7cc6ce32f8623ac9b6d5e323738680a0c5a76b08d6b3b91a954e4dfe0d3e2edbc16f1fc983255b51038101647257e56d80a0e775c043a018c157ca71266c2317ea46969c8855fd41927ad150cb06491b752f808080808080a0acebf31fb9d480ebffa9124c0ab88278758387f373ee35ebd774788206d4f0268080a03cd49a9233740289071eee441ea74efaa9e5b158edf504e80c02dd4c1ac6f7448080e2a03db0c169c0386eea811f84f409ba7520f113e805978996efe89009321440af740a"),
            destination = sp.address("KT1Tezooo1zzSmartPyzzSTATiCzzzyfC8eF")
        )
    )

    # The registry should be empty at the start
    scenario.verify(~bridge.data.registry.contains(eth_alice_address))

    # Teleport tokens back to Ethereum (Expected to fail, bridge does not have permission to burn the tokens)
    bridge.teleport(eth_address=eth_alice_address, amount=10).run(
        sender=sp.address("KT1Tezooo1zzSmartPyzzSTATiCzzzyfC8eF"), level=BLOCK_LEVEL_1
    ).run(valid=False, exception="FA2_NOT_OPERATOR")

    # Permit the bridge to burn tokens on your behalf.
    asset.update_operators(
        [sp.variant("add_operator", sp.record(owner=sp.address("KT1Tezooo1zzSmartPyzzSTATiCzzzyfC8eF"), operator=bridge.address, token_id=0))]
    ).run(sender=sp.address("KT1Tezooo1zzSmartPyzzSTATiCzzzyfC8eF"))

    # Teleport tokens back to Ethereum
    bridge.teleport(eth_address=eth_alice_address, amount=9).run(
        sender=sp.address("KT1Tezooo1zzSmartPyzzSTATiCzzzyfC8eF"), level=BLOCK_LEVEL_1
    )

    # Teleport tokens back to Ethereum (Expected to fail, not enough balance)
    bridge.teleport(eth_address=eth_bob_address, amount=2).run(
        sender=sp.address("KT1Tezooo1zzSmartPyzzSTATiCzzzyfC8eF"), level=BLOCK_LEVEL_1
    ).run(valid=False, exception="FA2_INSUFFICIENT_BALANCE")

    # Teleport tokens back to Ethereum (Expected to fail, not enough balance)
    bridge.teleport(eth_address=eth_bob_address, amount=1).run(
        sender=sp.address("KT1Tezooo1zzSmartPyzzSTATiCzzzyfC8eF"), level=BLOCK_LEVEL_1
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
