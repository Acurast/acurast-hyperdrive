import smartpy as sp

from contracts.tezos.IBCF_Eth_Validator import IBCF_Eth_Validator
from contracts.tezos.utils.bytes import int_of_bytes
from contracts.tezos.utils.rlp import item_length, payload_offset, num_items, to_list


@sp.add_test(name="IBCF_Eth_Validator")
def test():
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    claus = sp.test_account("claus")

    scenario = sp.test_scenario()
    ibcf = IBCF_Eth_Validator()
    ibcf.update_initial_storage(
        config=sp.record(
            administrator=admin.address,
            validators=sp.set(
                [
                    alice.address,
                    bob.address, claus.address
                ]
            ),
            eth_accounts=sp.set(
                [sp.bytes("0x9cc9bf39a84998089050a90087e597c26758685d")]
            ),
        ),
        storage_root=sp.big_map()
    )

    scenario += ibcf

    # Validate views
    scenario.verify(
        ibcf.nibbles_of_bytes(
            sp.record(
                bytes=sp.bytes("0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0"), skip=2
            )
        )
        == sp.bytes(
            "0x060f010a0b0f00070d0b0d0b070f0206020d000a07010006070d0a0d0c0402010f0e030d0f00"
        )
    )
    scenario.verify(
        ibcf.extract_nibble(
            sp.record(
                path=sp.bytes(
                    "0x6c2c8896c2375ca53a40019b1c64f2fb4cfbee5ff546cde64bf4bee12a4c0088"
                ),
                position=1,
            )
        )
        == 12
    )

    ibcf.submit_account_proof(
        account=sp.bytes("0x9cc9bf39a84998089050a90087e597c26758685d"),
        block_hash=sp.bytes(
            "0xb7964f87a97582605af695710ad252afa018a97384ba9438cf24e42fa9f0efc9"
        ),
        block_header=sp.bytes(
            "0xf90206a04880ecb6195d09477157e40eb5a15390cea5baf2f4d109915bcbdd30defdd5e0a01dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d4934794b2930b35844a230f00e51431acae96fe543a0347a0707ef8cb8652a70d509aa815f54add98a301327d7715329d4061f5e3ddb4c2e3a0ec467e94e90ba8053ac3d279fc0794161e84f4c5aa328208bfa0717090c1952fa07e7014d6a03e20602d4ff5e78a930443062d084bcf37be4e97bf7140cbdfdea5b901001c560054585a1a6044ac08040000a00400080011c0530100010200020800006a08804105403402000c004012042000000a0840080408811c022c082c0ca8040001184800516160230485903c0a4084005a070400991010811350c41180002001c411040a3a2000020540001004002830004c2022049658010005001140100104240900900146004009021000400400088840d080430005140009834c0000308c8206b200008812008f0c0180011b800004400001200000100800449c848605028430100200102484850840089621244444006001a2004010001000348982a0900010840001015c00900000018d11a150000a601600980c488c80000c0092411187087b0d49f4256b836d8e31837a121d83796724845c59ec0d8573696e6733a0841e4ff411a6665ad429a8cdd62fbfb544a3a475b9cda839cbf7cb3f81dad9e98810210d940048eddb"
        ),
        account_state_proof=sp.bytes(
            "0xf90d88f90211a0c8cd46af1b79ad42fa13a2f33da7bc1dbd2e5802fd416861f1fdc5a13e8940dda05bc496c81f8fcad9374386ce23cb05f12d0422dae3e84401870afb0f1beb4adaa0e235390a4551a62b1ac43a4a9be3c78f1e9ef04fe59cfcd087c72fccf0866e3aa0b4bb9cf76540eb61240b9c8a2d8fb0fdf2413544f13b177f5d2c69b6e61b1741a0a65176bed8f8f40eee1837776bb87683d0b2fa148ccc70e6d3da58df6761e813a02ad741a9e23d6ea154239a9e6a590800ed0e54b7baf83325f5a92e0b2db62b72a0d8ab9cecfc1e1d25e55031b9b31b10c9e8698ce4420bd921995c504932c91a21a01ec2e40343ae9dd8471f6ea9ffe48a4c99d42c664c05b0aa0a8c789b6bcd1342a08ad1a6dbc533492153df645f1ed30a7c4bc7327893e45634671e718ab53e69b1a08fa341768d72b9f310e2636225e0b9dbd906732d88eb3ccf786d9445c10511b5a05281ebf7637dc8e8d4b3fdd13a3587d48a7ea08d67035a09ec1fd2dd8fe62d7aa0681d05338c42c9c274eda6194d37bcd60630193b1fe4e21fd54ffda79ab436d7a0ebff770ac316f78cf27576a8e41e8d58599ed264fd68c2de1e13c9db02d2f156a0e056158ceadb4d6e97cf1e8406d311707f3860259413edd51c4ee170efa7fa1fa037497d736f3db69217cb3e72e04ea38faab08ed965caaa7701ddacb772bebacfa0ba76449bd47af7709f436294db9709983571648428c24cc8a4ff0d4fa3ef331880f90211a04c1573d31a649b166342b43381e8e47c0a2ad99dc5a5383917b69243f47073bea096b3a2b017f3351bb151d20ef8562dd08dc0c38cf291beb0d5a15c277798726ca0d34b6133fc44aeb8ee613c4d40d8b21df144f245c38908f9dd7fca75adf554c1a065e4fa744b40031dcb45a797ab998cf95fa2a2dca37dc0c09961e40cde9110d3a0a4b839236c148cb944e6a7ecd22b18ab23b28153bd5d100d1b5ed3392ddce0bda03e8be0ca57bfd9d6e7f69e3718592da3eff91940ca028104017252cf6c5031f1a07ba8d3fcecd43df88ca78b2dab753c9b4e1637b38ee1221ec731532ab2c4dc88a0e46aab7ee8d8ac4cb4a9040eaf6e777555067e83323d9ae80220127b4ffb3c40a00bfe0f6b4dc508fe880b21578741e9f61314c643d6e277c85e97534c6745e711a08fd2d3f729651038e6dd475d4d2029f312265fad65d855bf5fc636a8ddc8e910a098bba3a27066f10238dc0c7b82731320040cb63ca0ef34679d84a33acf98305ba0b2179a591fa45cb336e0965be12e6324ef54ebff27d4fbd0aa2527e3f03cd336a0ee114d413c735f572ec5f9b62e2640241909ca8539601e0bad7ad80bcbfd9ee3a0b4676801510fb9bc345fff7aa4ef857df379237a554c47e20009ea251b5f4022a0c0b99fb318bbac755d54f9c04848e27567d15964e9acc3f8f551c3efac499d79a0851302114fdcbe8f995cdc5526e756c206f34eeed821abb774925bd63202a59780f90211a04114b5f339b385f94c3ebaec9a39f7ab299c84f1c9615577008cfa34d46833cfa0891509cb86d182b78e38bbcbb7d56935fb49fd2d76f8c2835dac11f60642e6f3a01f33af279c8f72fe5905ff6abde54f42df733dd4d0b912dc749e84f2288be5d7a00dec13ec9f3ebb99348f9c2cf23da955609dee0cffda15f3b96509d835aef60ea0d207ae9d43f08b8ef4b6b312ee77eae3e6812b7923c164a89677b767b46ad06fa0919b1288c8bf767aaf8ca2ad205cb7415fe84eeafda0b83c089db8af8243ee0ca0ec5608754d2eaa9361ecdc3a5797d6149893eeb163d38f9d7262f9684449621fa0793bbd95653588c96d9d3ce0232b39d80dd0183e23b2ade4c54129eeb78091eea0bce0f33502ddd0dd2d557c0a7f4a4cc34df26248039f870296ca771bd2e0ba0ea0e703d943d47307d0c9b68504a691f5462727b393441aa5354f16d7c97c3a2acfa08652bf0edb8c57d65f85330aa59ea4d99f8b15409ae61da01de6f2d2429f5486a0e366b137c244e033720f72a3868046233e879d8ff69d62c8edd84920520e132ea05d0d64aab90b16eb9a30e99b903d8553f839a7df04230a77d7c55470bab36055a0c58dce64cf524460cc2264d3850e45a74b1c6bd1efcb574f51a482dabf88c58da0c71e861cac8b0a811a874c461df6f30d8516dfc5a7d7debae921c011c5a6e512a0bb70b02cd078729d3e5beb1cbd7c1aca78df91776db702d84e44dc01a3bef15d80f90211a0ff9f933de9900da961596607643224b45ea239d3478738e9dfb5bfb6ce835157a0f0fd47c84cbc75cbb246088bd8c3a9e0ff136e16449d3e873841999878801c7da07de8b4971586acc1262ecfbd46f999858b2d3f963c42609466dbe739e3f5f376a0d20606097e9076b24c845130bf6759f159ec2d3e95d75f215c2c435dad872430a014103161e9bbffea6afa58d5652a6152d27e77a6392cf79ae88911f2988ecc03a0a42a1df6c377ac100b114c4524b9e1dd7fd357811fc13da5fe30532bb4ca0f41a09ccdf76d0d76894e89ad962085f3a73bf3a9ba52d38e7cc4a5942ed2cd5ad573a0cefb669ec5d8fdd22d0e3ac31aa8d6a6ce6ce3bf6a6433d1ed8ab76f709d8b62a04eee36386e3ef435416559a27b374e684fa745fbc0142b2e31688691e3474322a072727b875115ab2049b8189291b61d0ab4119e21c389cfe7e50306e6023efa4da07bbbe14e56c22643cfc487fe3d07a0212d3ef14dbbef01b85b11d7a4f228d360a027ae43b03a73b682a4da899061ecf1fd1c0bc6c0b8421dbe1277d83a827ed2cca0b2b798dd42a60a3d35b86cfa6652d7c7030fc7a9d72d5ddd1ff1879978a211d5a09e3ecba335caf87706b52c80c20a10424ca703da335cae000d526c5c066e214ea00e79741831058d353c1026ae935f98e08cf979b61a45d46df712214ad9468deea09699ace2e29eb106d150fbdac22313ba326e72d0ead227dc6f60bb1393f2298480f90211a09e42e4d26a3ddf832fbd376055c19d99ee4309c91a7893e4bae526494b3e50f2a06168fabc77cfc3e1cd449b246eb311c223bf5456667e9af6de5e872ec3f7d1d5a07bf097d13c927e4dab5bebcda4d1bcdb290bbe8b42dec822768059b97d0148a4a0ff2fbc31c95c47b6f4a0b817f0ee2ece687cb1a6b918dbbd66e3502501b6d20fa0a848772c79e0733534ba77334b86d1c242a8d676f27dc993156b45a478e73880a01011dfed145677bef578c46d6d46a4e23c9b38e47246d46082990cbe6a9c02dda0dc83188546e3e96acbdcacda3a2bf54e6069fe10933c9c0a23403b8ce0935d0da07f62f2feb6d2ef09aa7b92284ff856f2cdebab33039838765174f7cb3ec9bb5ca00d4a262a059d17bc3f53182fef62f4dedcb13c4825c491640ab0ae4df71ab217a08eb84a6f051e4da23e779ed64c3ae650e59fdddc558cc6ec500e2b4f24d8523da041167ece41a040f26bb02a8009fd5512c27e29a2db71ec6b6c7ad7e621d81c77a0cd75570f97041719a5b6b2fbe9444c8fa5fa00e63fb200644537f7ff21547473a0253c9e9be058f010f3daa3eea825367cb9da21bcd5b39561dd6b597548bb1d51a037211e33ed3055c97f4df78d9a79dd5835c828f725103603a37e7b4cb14aca60a007e29805d8852d9a415290615f5291df823c9930dfb458a6520f99cd0036d870a04508db4e005c9feb3ecdd7dca11009256cbfab21edeb93def074e4b41dac162b80f901d1a0e8e020afe8aacb0f9bbadd534aa13abb0cb4de8c7e2ca554d6df7c2b507fed0a80a0da2d2ab7c069825fcb422f2a14aa072d14c76869104f1500f3f83e871c27417ea0a0b23808356f66db7097c098b87c6493d4c7111b45980524a412c8224a87e350a01a10f3f451eed17dc2cb98799fef6f46179c6742446dd3e73aacc339af81b4c1a02d50de9845254bed1fb80a1d8ed909c3ecd3df0544893fb042f9640c1d934ca5a07b3b50b860c3c7f8787c8d046c4e60f74535a1c2ec90c0f7dfc861041e28dc63a0ad46d416aa111d6cce7a5e5941354fab6773fb47b41468662855872710a98967a011a4370e53456f9ef5b277c6892acb3d05d5b5de266491d86fe1d401394fbf02a01f80eb207cef5c6103711e7b156d055015728dc6176bcd757754ba633d948782a01d34211de3dd11f5fd6fb1948ed6ca922f81c5caddacf14059bc09cec4ca4b99a08213883ca57a3353d4a516c69cd022c665b51599cfebf6c0e4a345a404eb4d7980a07f4a356bbf7d64d7e7883636090d56123784e790777e20d0febcc9a36d0471cca092956576f5de3738de2d061e244eabb2e14fc7c7922b3766e29ea9fe50d2158da02ddd89bad44e0c8384cf0780f00a07eb3a8df167cffda1c1a6f8ed3b0429fa9b80f8718080808080808080a001bcc1bfa4306681ba90951d2547e6b9c6aeaad81f1cb4394f696e4f1b941f7ca037fb984c6c1e14e4e1d4e98d6d45cabe83f878f3a36d9435a5cbce1b3634916c80a0e6b7500ebd2b6b90e2c0c2208e5e7a85e8bd4b7392844d81864ddd961db07d948080808080e216a0e886040251f67ebad1399818dd16d3879e7b4ce836ccdd16562e640bd7462c47f85180a0d12e19add3399af92b890ec9eeb5c9b9152f093d20600fe587e6472314a37afe80808080808080808080a0315279f9bc0eb2ac0827d79d4b2ede9acc71c485fd3bf993c783e00c5b76fc4e80808080f8659c32375ca53a40019b1c64f2fb4cfbee5ff546cde64bf4bee12a4c0088b846f8440180a0c14953a64f69632619636fbdf327e883436b9fd1b1025220e50fb70ab7d2e2a8a0f7cf6232b8d655b92268b3565325e8897f2f82d65a4eaaf4e78fcef04e8fee6a"
        ),
    ).run(sender=alice.address)

    scenario.verify(
        ibcf.get_storage(
            sp.record(
                account=sp.bytes("0x9cc9bf39a84998089050a90087e597c26758685d"),
                block_number=7179825,
                storage_slot=sp.bytes(
                    "0x0000000000000000000000000000000000000000000000000000000000000000"
                ),
                storage_proof=sp.bytes(
                    "0xf879f8518080a036bb5f2fd6f99b186600638644e2f0396989955e201672f7e81e8c8f466ed5b98080808080808080808080a0f70bd5b82fa5222804070e8400da42b4ae39eb527a42f19106acf68ea58a4eb38080e5a0390decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563838204d2"
                ),
            )
        ) == sp.bytes("0x8204d2")
    )

    scenario.verify(sp.build_lambda(int_of_bytes)(sp.bytes("0x0211")) == 529)
    scenario.verify(
        sp.build_lambda(item_length)(
            sp.bytes(
                "0xf90211a0c8cd46af1b79ad42fa13a2f33da7bc1dbd2e5802fd416861f1fdc5a13e8940dda05bc496c81f8fcad9374386ce23cb05f12d0422dae3e84401870afb0f1beb4adaa0e235390a4551a62b1ac43a4a9be3c78f1e9ef04fe59cfcd087c72fccf0866e3aa0b4bb9cf76540eb61240b9c8a2d8fb0fdf2413544f13b177f5d2c69b6e61b1741a0a65176bed8f8f40eee1837776bb87683d0b2fa148ccc70e6d3da58df6761e813a02ad741a9e23d6ea154239a9e6a590800ed0e54b7baf83325f5a92e0b2db62b72a0d8ab9cecfc1e1d25e55031b9b31b10c9e8698ce4420bd921995c504932c91a21a01ec2e40343ae9dd8471f6ea9ffe48a4c99d42c664c05b0aa0a8c789b6bcd1342a08ad1a6dbc533492153df645f1ed30a7c4bc7327893e45634671e718ab53e69b1a08fa341768d72b9f310e2636225e0b9dbd906732d88eb3ccf786d9445c10511b5a05281ebf7637dc8e8d4b3fdd13a3587d48a7ea08d67035a09ec1fd2dd8fe62d7aa0681d05338c42c9c274eda6194d37bcd60630193b1fe4e21fd54ffda79ab436d7a0ebff770ac316f78cf27576a8e41e8d58599ed264fd68c2de1e13c9db02d2f156a0e056158ceadb4d6e97cf1e8406d311707f3860259413edd51c4ee170efa7fa1fa037497d736f3db69217cb3e72e04ea38faab08ed965caaa7701ddacb772bebacfa0ba76449bd47af7709f436294db9709983571648428c24cc8a4ff0d4fa3ef331880"
            )
        )
        == 532
    )
    scenario.verify(
        sp.build_lambda(payload_offset)(
            sp.bytes(
                "0xf90211a0c8cd46af1b79ad42fa13a2f33da7bc1dbd2e5802fd416861f1fdc5a13e8940dda05bc496c81f8fcad9374386ce23cb05f12d0422dae3e84401870afb0f1beb4adaa0e235390a4551a62b1ac43a4a9be3c78f1e9ef04fe59cfcd087c72fccf0866e3aa0b4bb9cf76540eb61240b9c8a2d8fb0fdf2413544f13b177f5d2c69b6e61b1741a0a65176bed8f8f40eee1837776bb87683d0b2fa148ccc70e6d3da58df6761e813a02ad741a9e23d6ea154239a9e6a590800ed0e54b7baf83325f5a92e0b2db62b72a0d8ab9cecfc1e1d25e55031b9b31b10c9e8698ce4420bd921995c504932c91a21a01ec2e40343ae9dd8471f6ea9ffe48a4c99d42c664c05b0aa0a8c789b6bcd1342a08ad1a6dbc533492153df645f1ed30a7c4bc7327893e45634671e718ab53e69b1a08fa341768d72b9f310e2636225e0b9dbd906732d88eb3ccf786d9445c10511b5a05281ebf7637dc8e8d4b3fdd13a3587d48a7ea08d67035a09ec1fd2dd8fe62d7aa0681d05338c42c9c274eda6194d37bcd60630193b1fe4e21fd54ffda79ab436d7a0ebff770ac316f78cf27576a8e41e8d58599ed264fd68c2de1e13c9db02d2f156a0e056158ceadb4d6e97cf1e8406d311707f3860259413edd51c4ee170efa7fa1fa037497d736f3db69217cb3e72e04ea38faab08ed965caaa7701ddacb772bebacfa0ba76449bd47af7709f436294db9709983571648428c24cc8a4ff0d4fa3ef331880"
            )
        )
        == 3
    )
    scenario.verify(
        sp.build_lambda(num_items)(
            sp.bytes(
                "0xf90211a0c8cd46af1b79ad42fa13a2f33da7bc1dbd2e5802fd416861f1fdc5a13e8940dda05bc496c81f8fcad9374386ce23cb05f12d0422dae3e84401870afb0f1beb4adaa0e235390a4551a62b1ac43a4a9be3c78f1e9ef04fe59cfcd087c72fccf0866e3aa0b4bb9cf76540eb61240b9c8a2d8fb0fdf2413544f13b177f5d2c69b6e61b1741a0a65176bed8f8f40eee1837776bb87683d0b2fa148ccc70e6d3da58df6761e813a02ad741a9e23d6ea154239a9e6a590800ed0e54b7baf83325f5a92e0b2db62b72a0d8ab9cecfc1e1d25e55031b9b31b10c9e8698ce4420bd921995c504932c91a21a01ec2e40343ae9dd8471f6ea9ffe48a4c99d42c664c05b0aa0a8c789b6bcd1342a08ad1a6dbc533492153df645f1ed30a7c4bc7327893e45634671e718ab53e69b1a08fa341768d72b9f310e2636225e0b9dbd906732d88eb3ccf786d9445c10511b5a05281ebf7637dc8e8d4b3fdd13a3587d48a7ea08d67035a09ec1fd2dd8fe62d7aa0681d05338c42c9c274eda6194d37bcd60630193b1fe4e21fd54ffda79ab436d7a0ebff770ac316f78cf27576a8e41e8d58599ed264fd68c2de1e13c9db02d2f156a0e056158ceadb4d6e97cf1e8406d311707f3860259413edd51c4ee170efa7fa1fa037497d736f3db69217cb3e72e04ea38faab08ed965caaa7701ddacb772bebacfa0ba76449bd47af7709f436294db9709983571648428c24cc8a4ff0d4fa3ef331880"
            )
        )
        == 17
    )

    scenario.show(
        sp.build_lambda(to_list)(
            sp.bytes(
                "0xf90211a0c8cd46af1b79ad42fa13a2f33da7bc1dbd2e5802fd416861f1fdc5a13e8940dda05bc496c81f8fcad9374386ce23cb05f12d0422dae3e84401870afb0f1beb4adaa0e235390a4551a62b1ac43a4a9be3c78f1e9ef04fe59cfcd087c72fccf0866e3aa0b4bb9cf76540eb61240b9c8a2d8fb0fdf2413544f13b177f5d2c69b6e61b1741a0a65176bed8f8f40eee1837776bb87683d0b2fa148ccc70e6d3da58df6761e813a02ad741a9e23d6ea154239a9e6a590800ed0e54b7baf83325f5a92e0b2db62b72a0d8ab9cecfc1e1d25e55031b9b31b10c9e8698ce4420bd921995c504932c91a21a01ec2e40343ae9dd8471f6ea9ffe48a4c99d42c664c05b0aa0a8c789b6bcd1342a08ad1a6dbc533492153df645f1ed30a7c4bc7327893e45634671e718ab53e69b1a08fa341768d72b9f310e2636225e0b9dbd906732d88eb3ccf786d9445c10511b5a05281ebf7637dc8e8d4b3fdd13a3587d48a7ea08d67035a09ec1fd2dd8fe62d7aa0681d05338c42c9c274eda6194d37bcd60630193b1fe4e21fd54ffda79ab436d7a0ebff770ac316f78cf27576a8e41e8d58599ed264fd68c2de1e13c9db02d2f156a0e056158ceadb4d6e97cf1e8406d311707f3860259413edd51c4ee170efa7fa1fa037497d736f3db69217cb3e72e04ea38faab08ed965caaa7701ddacb772bebacfa0ba76449bd47af7709f436294db9709983571648428c24cc8a4ff0d4fa3ef331880"
            )
        )
    )
