import smartpy as sp
from contracts.tezos.MMR_Validator import merge_sort, merge_maps, MMR_Validator, MMR, MultiProof, Iterator

@sp.add_test(name = "MMR_Validator")
def test():
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    claus = sp.test_account("claus")

    c1 = MMR_Validator()
    c1.update_initial_storage(
        config=sp.record(
            governance=admin.address,
            validators=sp.set([alice.address, bob.address, claus.address]),
            minimum_endorsements=2,
        ),
        current_snapshot=2,
        snapshot_submissions=sp.map(),
        root=sp.big_map({
            1: sp.bytes("0x5aac4bad5c6a9014429b7e19ec0e5cd059d28d697c9cdd3f71e78cb6bfbd2600")
        }),
    )
    scenario = sp.test_scenario()
    scenario += c1

    scenario.h1("MMR.difference")
    difference_lambda = sp.build_lambda(lambda arg: MMR.difference(arg.one, arg.two))
    scenario.verify_equal(
        difference_lambda(
            sp.record(
                one = {0 : 1},
                two = {0 : 0},
            )
        ),
        sp.set([1])
    )
    scenario.verify_equal(
        difference_lambda(
            sp.record(
                one = {0 : 1, 1: 0},
                two = {0 : 0, 1: 1},
            )
        ),
        sp.set([])
    )
    scenario.verify(sp.build_lambda(lambda x: MMR.pos_to_height(x))(100) == 2)
    scenario.verify_equal(sp.build_lambda(lambda x: MMR.get_peaks(x))(25), [14, 21, 24])

    leaves_for_peak_lambda = sp.build_lambda(lambda arg: MMR.leaves_for_peak(arg.leaves, arg.peak))
    scenario.verify_equal(
        leaves_for_peak_lambda(
            sp.record(
                leaves = sp.map({
                    0 : sp.record(
                        hash = sp.bytes('0x2b97a4b75a93aa1ac8581fac0f7d4ab42406569409a737bdf9de584903b372c5'),
                        k_index = 2,
                        mmr_pos = 3
                    ),
                    1 : sp.record(
                        hash = sp.bytes('0xd279eb4bf22b2aeded31e65a126516215a9d93f83e3e425fdcd1a05ab347e535'),
                        k_index = 5,
                        mmr_pos = 8
                    ),
                    2 : sp.record(
                        hash = sp.bytes('0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8'),
                        k_index = 0,
                        mmr_pos = 15
                    ),
                    3 : sp.record(
                        hash = sp.bytes('0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795'),
                        k_index = 2,
                        mmr_pos = 18
                    ),
                    4 : sp.record(
                        hash = sp.bytes('0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9'),
                        k_index = 0,
                        mmr_pos = 22
                    )
                }),
                peak = 14,
            )
        ),
        (
            sp.map({
                0 : sp.record(
                    hash = sp.bytes('0x2b97a4b75a93aa1ac8581fac0f7d4ab42406569409a737bdf9de584903b372c5'),
                    k_index = 2,
                    mmr_pos = 3
                ),
                1 : sp.record(
                    hash = sp.bytes('0xd279eb4bf22b2aeded31e65a126516215a9d93f83e3e425fdcd1a05ab347e535'),
                    k_index = 5,
                    mmr_pos = 8
                ),

            }),
            sp.map({
                0 : sp.record(
                    hash = sp.bytes('0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8'),
                    k_index = 0,
                    mmr_pos = 15
                ),
                1 : sp.record(
                    hash = sp.bytes('0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795'),
                    k_index = 2,
                    mmr_pos = 18
                ),
                2 : sp.record(
                    hash = sp.bytes('0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9'),
                    k_index = 0,
                    mmr_pos = 22
                )
            })
        )
    )

    scenario.verify(
        MultiProof.calculate_root(
            (
                sp.map(
                    {
                        0: sp.map(
                            {
                                0 : sp.record(
                                    k_index = 1,
                                    hash = sp.bytes("0x7463c9b814b5d9081938e21346fe8bf81a9a9a0dcfa7bcc03b644a361e395a3b")
                                ),
                            }
                        )
                    }
                ),
                sp.map(
                    {
                        0 : sp.record(
                            k_index = 0,
                            hash = sp.bytes("0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9")
                        ),
                    }
                )
            )
        ) == sp.bytes("0xea5eb4c6212f178939883a6f804eef46074a83e4f258e072b600e9baf154864a")
    )

    scenario.verify(
        MultiProof.calculate_root(
            (
                sp.map(
                    {
                        0: sp.map(
                            {
                                0 : sp.record(
                                    k_index = 1,
                                    hash = sp.bytes("0x754310be011a7a378b07fa7cbac39dbedcadf645c518ddec58deeaa8c29e0634")
                                ),
                                1 : sp.record(
                                    k_index = 3,
                                    hash = sp.bytes("0x06be3c46e5a06d7b3e438a9d698f4319dc628624a63e484d97f00b92d09edce7")
                                ),
                            }
                        ),
                        1: sp.map()
                    }
                ),
                sp.map(
                    {
                        0 : sp.record(
                            k_index = 0,
                            hash = sp.bytes("0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8")
                        ),
                        1 : sp.record(
                            k_index = 2,
                            hash = sp.bytes("0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795")
                        ),
                    }
                )
            )
        ) == sp.bytes("0xf0491ae550cf2109665e07df91118e03d4cf23c59b8b4a4dd8dff0726cc86ae8")
    )

    calculate_peak_root_lambda = sp.build_lambda(lambda arg: MMR.calculate_peak_root(arg.one, Iterator.new(arg.two, arg.three), arg.four))
    scenario.verify_equal(
        calculate_peak_root_lambda(
            sp.record(
                one = sp.map(
                    {
                        0: sp.record(
                            k_index = 0,
                            mmr_pos = 22,
                            hash = sp.bytes("0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9")
                        ),
                    }
                ),
                two = 6,
                three = sp.map(
                    {
                        0: sp.bytes("0xa4a7208a40e95acaf2fe1a3c675b1b5d8c341060e4f179b76ba79493582a95a6"),
                        1: sp.bytes("0x989a7025bda9312b19569d9e84e33a624e7fc007e54db23b6758d5f819647071"),
                        2: sp.bytes("0xfc5b56233029d71e7e9aff8e230ff491475dee2d8074b27d5fecf8f5154d7c8d"),
                        3: sp.bytes("0x37db026959b7bafb26c0d292ecd69c24df5eab845d9625ac5301324402938f25"),
                        4: sp.bytes("0x754310be011a7a378b07fa7cbac39dbedcadf645c518ddec58deeaa8c29e0634"),
                        5: sp.bytes("0x06be3c46e5a06d7b3e438a9d698f4319dc628624a63e484d97f00b92d09edce7"),
                        6: sp.bytes("0x7463c9b814b5d9081938e21346fe8bf81a9a9a0dcfa7bcc03b644a361e395a3b"),
                    }
                ),
                four = 24
            )
        ),
        sp.bytes("0xea5eb4c6212f178939883a6f804eef46074a83e4f258e072b600e9baf154864a")
    )
    scenario.verify_equal(
        calculate_peak_root_lambda(
            sp.record(
                one = sp.map(
                    {
                        0: sp.record(
                            k_index = 0,
                            mmr_pos = 15,
                            hash = sp.bytes("0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8")
                        ),
                        1: sp.record(
                            k_index = 2,
                            mmr_pos = 18,
                            hash = sp.bytes("0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795")
                        ),
                    }
                ),
                two = 4,
                three = sp.map(
                    {
                        0: sp.bytes("0xa4a7208a40e95acaf2fe1a3c675b1b5d8c341060e4f179b76ba79493582a95a6"),
                        1: sp.bytes("0x989a7025bda9312b19569d9e84e33a624e7fc007e54db23b6758d5f819647071"),
                        2: sp.bytes("0xfc5b56233029d71e7e9aff8e230ff491475dee2d8074b27d5fecf8f5154d7c8d"),
                        3: sp.bytes("0x37db026959b7bafb26c0d292ecd69c24df5eab845d9625ac5301324402938f25"),
                        4: sp.bytes("0x754310be011a7a378b07fa7cbac39dbedcadf645c518ddec58deeaa8c29e0634"),
                        5: sp.bytes("0x06be3c46e5a06d7b3e438a9d698f4319dc628624a63e484d97f00b92d09edce7"),
                        6: sp.bytes("0x7463c9b814b5d9081938e21346fe8bf81a9a9a0dcfa7bcc03b644a361e395a3b"),
                    }
                ),
                four = 21
            )
        ),
        sp.bytes("0xf0491ae550cf2109665e07df91118e03d4cf23c59b8b4a4dd8dff0726cc86ae8")
    )
    scenario.verify_equal(
        calculate_peak_root_lambda(
            sp.record(
                one = sp.map(
                    {
                        0: sp.record(
                            k_index = 2,
                            mmr_pos = 3,
                            hash = sp.bytes("0x2b97a4b75a93aa1ac8581fac0f7d4ab42406569409a737bdf9de584903b372c5")
                        ),
                        1: sp.record(
                            k_index = 5,
                            mmr_pos = 8,
                            hash = sp.bytes("0xd279eb4bf22b2aeded31e65a126516215a9d93f83e3e425fdcd1a05ab347e535")
                        ),
                    }
                ),
                two = 0,
                three = sp.map(
                    {
                        0: sp.bytes("0xa4a7208a40e95acaf2fe1a3c675b1b5d8c341060e4f179b76ba79493582a95a6"),
                        1: sp.bytes("0x989a7025bda9312b19569d9e84e33a624e7fc007e54db23b6758d5f819647071"),
                        2: sp.bytes("0xfc5b56233029d71e7e9aff8e230ff491475dee2d8074b27d5fecf8f5154d7c8d"),
                        3: sp.bytes("0x37db026959b7bafb26c0d292ecd69c24df5eab845d9625ac5301324402938f25"),
                        4: sp.bytes("0x754310be011a7a378b07fa7cbac39dbedcadf645c518ddec58deeaa8c29e0634"),
                        5: sp.bytes("0x06be3c46e5a06d7b3e438a9d698f4319dc628624a63e484d97f00b92d09edce7"),
                        6: sp.bytes("0x7463c9b814b5d9081938e21346fe8bf81a9a9a0dcfa7bcc03b644a361e395a3b"),
                    }
                ),
                four = 14
            )
        ),
        sp.bytes("0x60d08524143a468298306250e9219a97584c9b0dc4dd0bd9c302e1a380bba744")
    )

    calculate_root_lambda = sp.build_lambda(lambda arg: MMR.calculate_root(arg.one, arg.two, arg.three))
    scenario.verify(
        calculate_root_lambda(
            sp.record(
                one = sp.map(
                    {
                        0: sp.bytes("0xa4a7208a40e95acaf2fe1a3c675b1b5d8c341060e4f179b76ba79493582a95a6"),
                        1: sp.bytes("0x989a7025bda9312b19569d9e84e33a624e7fc007e54db23b6758d5f819647071"),
                        2: sp.bytes("0xfc5b56233029d71e7e9aff8e230ff491475dee2d8074b27d5fecf8f5154d7c8d"),
                        3: sp.bytes("0x37db026959b7bafb26c0d292ecd69c24df5eab845d9625ac5301324402938f25"),
                        4: sp.bytes("0x754310be011a7a378b07fa7cbac39dbedcadf645c518ddec58deeaa8c29e0634"),
                        5: sp.bytes("0x06be3c46e5a06d7b3e438a9d698f4319dc628624a63e484d97f00b92d09edce7"),
                        6: sp.bytes("0x7463c9b814b5d9081938e21346fe8bf81a9a9a0dcfa7bcc03b644a361e395a3b"),
                    }
                ),
                two = sp.map(
                    {
                        0: sp.record(
                            k_index = 2,
                            mmr_pos = 3,
                            hash = sp.bytes("0x2b97a4b75a93aa1ac8581fac0f7d4ab42406569409a737bdf9de584903b372c5")
                        ),
                        1: sp.record(
                            k_index = 5,
                            mmr_pos = 8,
                            hash = sp.bytes("0xd279eb4bf22b2aeded31e65a126516215a9d93f83e3e425fdcd1a05ab347e535")
                        ),
                        2: sp.record(
                            k_index = 0,
                            mmr_pos = 15,
                            hash = sp.bytes("0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8")
                        ),
                        3: sp.record(
                            k_index = 2,
                            mmr_pos = 18,
                            hash = sp.bytes("0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795")
                        ),
                        4: sp.record(
                            k_index = 0,
                            mmr_pos = 22,
                            hash = sp.bytes("0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9")
                        )
                    }
                ),
                three = 25
            )
        ) == sp.bytes("0x5aac4bad5c6a9014429b7e19ec0e5cd059d28d697c9cdd3f71e78cb6bfbd2600")
    )

    scenario.verify_equal(
        merge_sort(
            merge_maps(
                (
                    sp.map(
                        {
                            0 : sp.record(
                                k_index = 1,
                                hash = sp.bytes("0x1000000000000000000000000000000000000000000000000000000000000000")
                            ),
                            1: sp.record(
                                k_index = 2,
                                hash = sp.bytes("0x2000000000000000000000000000000000000000000000000000000000000000")
                            ),
                        }
                    ),
                    sp.map(
                        {
                            0 : sp.record(
                                k_index = 5,
                                hash = sp.bytes("0x5000000000000000000000000000000000000000000000000000000000000000")
                            ),
                            1: sp.record(
                                k_index = 3,
                                hash = sp.bytes("0x3000000000000000000000000000000000000000000000000000000000000000")
                            )
                        }
                    )
                )
            )
        ),
        sp.map(
            {
                0 : sp.record(
                    k_index = 1,
                    hash = sp.bytes("0x1000000000000000000000000000000000000000000000000000000000000000")
                ),
                1: sp.record(
                    k_index = 2,
                    hash = sp.bytes("0x2000000000000000000000000000000000000000000000000000000000000000")
                ),
                2: sp.record(
                    k_index = 3,
                    hash = sp.bytes("0x3000000000000000000000000000000000000000000000000000000000000000")
                ),
                3 : sp.record(
                    k_index = 5,
                    hash = sp.bytes("0x5000000000000000000000000000000000000000000000000000000000000000")
                ),
            }
        )
    )
    scenario.show(
        MultiProof.calculate_root(
            (
                sp.map(
                    {
                        0: sp.map(
                            {
                                0 : sp.record(
                                    k_index = 3,
                                    hash = sp.bytes("0x065aff9602a25b0538643a8a81fa29fdaba2ae568b61ac217cea9233798ab14a")
                                ),
                            }
                        ),
                        1: sp.map(
                            {
                                0: sp.record(
                                    k_index = 0,
                                    hash = sp.bytes("0x95e6f12aa5a8a8f4c4910166152849834cc388a8151c43298b99af0de7125e99")
                                ),
                            }
                        ),
                        2: sp.map(
                            {
                                0: sp.record(
                                    k_index = 1,
                                    hash = sp.bytes("0xe43a34012e0a45ce6075ac377bf0a35ba316c9f324cafb9016e0e58032c01ec8")
                                ),
                            }
                        ),
                        3: sp.map(
                            {
                                0: sp.record(
                                    k_index = 1,
                                    hash = sp.bytes("0xd21d5d4bde2d68d4179093c889138cefca3eb4e95e91554876153832848c8887")
                                ),
                            }
                        ),
                        4: sp.map(
                            {
                                0: sp.record(
                                    k_index = 1,
                                    hash = sp.bytes("0x427e513e4be7a3b801b69ac49ffbd435a0e46114e2ab5e1258518017d4a6c595")
                                ),
                            }
                        ),
                        5: sp.map(
                            {
                                0: sp.record(
                                    k_index = 1,
                                    hash = sp.bytes("0x7da58cfe1038b71aeef0b0f22ecaea7d6368916f5214a18fd971bd34c6ab86b1")
                                ),
                            }
                        ),
                        6: sp.map(
                            {
                                0: sp.record(
                                    k_index = 1,
                                    hash = sp.bytes("0x479f391367a51f2b8f14ee907ebd21e3c7d1da2ea63946335e4ed13e4e882e23")
                                ),
                            }
                        ),
                        7: sp.map(
                            {
                                0: sp.record(
                                    k_index = 1,
                                    hash = sp.bytes("0x469d3885ec0cae3f1172312460226cfbc0a4140230f8761d0fb6bde6d83d8408")
                                )
                            }
                        ),
                    }
                ),
                sp.map(
                    {
                        0 : sp.record(
                            k_index = 2,
                            hash = sp.bytes("0x0302a35dfed8f03aa94acf2a4e0f01909591e0e39baeacb2ba5fc9ab83a514ff")
                        ),
                    }
                )
            )
        )
    )

    scenario.verify(
        c1.verify_proof(
            sp.record(
                snapshot = 1,
                proof = [
                    sp.bytes("0xa4a7208a40e95acaf2fe1a3c675b1b5d8c341060e4f179b76ba79493582a95a6"),
                    sp.bytes("0x989a7025bda9312b19569d9e84e33a624e7fc007e54db23b6758d5f819647071"),
                    sp.bytes("0xfc5b56233029d71e7e9aff8e230ff491475dee2d8074b27d5fecf8f5154d7c8d"),
                    sp.bytes("0x37db026959b7bafb26c0d292ecd69c24df5eab845d9625ac5301324402938f25"),
                    sp.bytes("0x754310be011a7a378b07fa7cbac39dbedcadf645c518ddec58deeaa8c29e0634"),
                    sp.bytes("0x06be3c46e5a06d7b3e438a9d698f4319dc628624a63e484d97f00b92d09edce7"),
                    sp.bytes("0x7463c9b814b5d9081938e21346fe8bf81a9a9a0dcfa7bcc03b644a361e395a3b"),
                ],
                leaves = [
                    sp.record(
                        k_index = 2,
                        mmr_pos = 3,
                        hash = sp.bytes("0x2b97a4b75a93aa1ac8581fac0f7d4ab42406569409a737bdf9de584903b372c5")
                    ),
                    sp.record(
                        k_index = 5,
                        mmr_pos = 8,
                        hash = sp.bytes("0xd279eb4bf22b2aeded31e65a126516215a9d93f83e3e425fdcd1a05ab347e535")
                    ),
                    sp.record(
                        k_index = 0,
                        mmr_pos = 15,
                        hash = sp.bytes("0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8")
                    ),
                    sp.record(
                        k_index = 2,
                        mmr_pos = 18,
                        hash = sp.bytes("0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795")
                    ),
                    sp.record(
                        k_index = 0,
                        mmr_pos = 22,
                        hash = sp.bytes("0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9")
                    )
                ],
                mmr_size = 25
            )
        ) == True
    )

    return
    c1.receive_message(
        sp.record(
            root_state_hash = sp.bytes("0x4675ae398f3103976ea5cf164d0905918da2ae553369f8da48b9e950061884ac"),
            proof = [
                sp.variant("message", sp.bytes("0x693880717109924bae62d4144261a2a3afac1ccaa308309fee2938079e99d67d")),
                sp.variant("message", sp.bytes("0x35cd30aac96257a4872c09cf127de11725619db9b358d278218673d51bcdf41e")),
                sp.variant("merge_op", True),
                sp.variant("node", sp.bytes("0x8397260b06b5df993362d69754c7cbb7ef2a276d93eb379fecd7b279db6cd71f")),
                sp.variant("merge_op", True),
                sp.variant("node", sp.bytes("0x24bbed227accc2579576b96bf7b85bf5d358c0f97a7eba44202800ef261f8070")),
                sp.variant("merge_op", False),
                sp.variant("message", sp.bytes("0x04971f9be3a513c45d3eba8060c498613aa56432858729a63abd54f47fc34b6d")),
                sp.variant("node", sp.bytes("0x4eaf0939c71305e286db9af111303bdfe5f40df6eba2f9e5baf2dbfeefbfc674")),
                sp.variant("merge_op", True),
                sp.variant("node", sp.bytes("0xc2c1b96679f2b218e7b10a418fcdec9915a32d0b7b29601c53e438dbdda3bee3")),
                sp.variant("merge_op", True),
                sp.variant("merge_op", True),
            ]
        )
    )

    c1.receive_message(
        sp.record(
            root_state_hash = sp.bytes("0x5a656e4c7c27b1fc8e494bd5192d6fb4d4dbc2f373198f923324798d1c9320b2"),
            proof = [
                sp.variant("message", sp.bytes("0x8fbce10127c61db80e947db275ad8df1bddab6287280210533c745d6cf5ed8f4")),
                sp.variant("message", sp.bytes("0xee9a1c4750224c5ee4d7b54198cab1441b99fab8db79d5d04508320f52cd5afa")),
                sp.variant("merge_op", True),
                sp.variant("node", sp.bytes("0x720974feef96c21b8b8ed769d2efb7bf24482758320506dc53b109e1110f9299")),
                sp.variant("merge_op", False),
                sp.variant("message", sp.bytes("0x4eb1379c9db1caf818e3bce702f747a8fd0d52180a727de35a3245d609edea21")),
                sp.variant("message", sp.bytes("0x4e9c4d99df5b8c0add2aa46f69f34fbdee856aacc5f9ea22dcc096e5133c9689")),
                sp.variant("merge_op", False),
                sp.variant("node", sp.bytes("0xe5a7d4c147802d338de3f681039a8cc985c872ba4610a50af255812c600a6e0a")),
                sp.variant("merge_op", True),
                sp.variant("merge_op", False),
                sp.variant("message", sp.bytes("0xc2c1b96679f2b218e7b10a418fcdec9915a32d0b7b29601c53e438dbdda3bee3")),
                sp.variant("message", sp.bytes("0x33675f8b42d4e37481c4eb1f80e3722d18e1cffa68ee0ee6ca6d8bb2292018b8")),
                sp.variant("merge_op", False),
                sp.variant("node", sp.bytes("0xa6cd4951c2ec7554885b131bd0fcc02ce4edb2c3d4d806645a0a08dde095a97e")),
                sp.variant("merge_op", True),
                sp.variant("message", sp.bytes("0xa34eaa9eb82b4d72e4ec0a11290f822bb198c503d9d693983e0149280d9daea1")),
                sp.variant("message", sp.bytes("0x03dfa2d3646e11bca34b2f1cfc193bea9401e4a43c867410989066b98aa68f1f")),
                sp.variant("merge_op", False),
                sp.variant("node", sp.bytes("0x3ce28c9c0a58eb611441e77d10558c64d35941ff962409c72e847d33cb2dfaa9")),
                sp.variant("merge_op", False),
                sp.variant("merge_op", False),
                sp.variant("merge_op", False),
                sp.variant("node", sp.bytes("0x28f60a4850763191fa8227431f5ed45c30d251d3d5184b29a1cc2487a976b847")),
                sp.variant("node", sp.bytes("0x6dd25ab3f046988328e096baf8c0485948f8c9654c766cec25c0b7c8106b4a1e")),
                sp.variant("node", sp.bytes("0x47176934d576cf91abc518355142a71133c30077fb00207e9748d738fcace535")),
                sp.variant("merge_op", True),
                sp.variant("merge_op", True),
                sp.variant("merge_op", True),
            ]
        )
    )
