import smartpy as sp
from contracts.tezos.MMR_Validator import (
    merge_sort,
    merge_maps,
    MMR_Validator,
    MMR,
    MultiProof,
    Iterator,
)


@sp.add_test(name="MMR_Validator")
def test():
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    claus = sp.test_account("claus")

    c1 = MMR_Validator()
    c1.update_initial_storage(
        config=sp.record(
            governance_address=admin.address,
            validators=sp.set([alice.address, bob.address, claus.address]),
            minimum_endorsements=2,
        ),
        current_snapshot=2,
        snapshot_submissions=sp.map(),
        root=sp.big_map(
            {
                1: sp.bytes(
                    "0x5aac4bad5c6a9014429b7e19ec0e5cd059d28d697c9cdd3f71e78cb6bfbd2600"
                ),
                2: sp.bytes(
                    "0xf9ff75def54e55e0e7267f360278c6ced1afc8e5aa3c7ccdbdea92104898642c"
                ),
                3: sp.bytes(
                    "0x35c28b0a4291ceb22f054934109750d531f296271e260819eb41170a34af8b07"
                ),
                4: sp.bytes(
                    "0x6febfc341bd3acea5b8e961dd7ab0c2f71578d34afaf4ca7d84443b32824685b"
                ),
                5: sp.bytes(
                    "0x1fe10aa430fefd6713e347417d32ad71502b81cb3082e41ab71be5e8f15bb661"
                ),
                6: sp.bytes(
                    "0x1a1f7892b263550d320cf63bb6594281ecab69a30418a9d27f37cc7eef930652"
                ),
            }
        ),
    )
    scenario = sp.test_scenario()
    scenario += c1

    scenario.h1("MMR.leaf_count_to_mmr_size")
    leaf_count_to_mmr_size_lambda = sp.build_lambda(
        lambda arg: MMR.leaf_count_to_mmr_size(arg)
    )
    scenario.verify(leaf_count_to_mmr_size_lambda(7) == 11)

    scenario.h1("MMR.difference")
    difference_lambda = sp.build_lambda(lambda arg: MMR.difference(arg.one, arg.two))
    scenario.verify_equal(
        difference_lambda(
            sp.record(
                one={0: 1},
                two={0: 0},
            )
        ),
        sp.set([1]),
    )
    scenario.verify_equal(
        difference_lambda(
            sp.record(
                one={0: 1, 1: 0},
                two={0: 0, 1: 1},
            )
        ),
        sp.set([]),
    )
    scenario.verify(sp.build_lambda(lambda x: MMR.pos_to_height(x))(100) == 2)
    scenario.verify_equal(sp.build_lambda(lambda x: MMR.get_peaks(x))(25), [14, 21, 24])

    leaves_for_peak_lambda = sp.build_lambda(
        lambda arg: MMR.leaves_for_peak(arg.leaves, arg.peak)
    )
    scenario.verify_equal(
        leaves_for_peak_lambda(
            sp.record(
                leaves=sp.map(
                    {
                        0: sp.record(
                            hash=sp.bytes(
                                "0x2b97a4b75a93aa1ac8581fac0f7d4ab42406569409a737bdf9de584903b372c5"
                            ),
                            mmr_pos=3,
                        ),
                        1: sp.record(
                            hash=sp.bytes(
                                "0xd279eb4bf22b2aeded31e65a126516215a9d93f83e3e425fdcd1a05ab347e535"
                            ),
                            mmr_pos=8,
                        ),
                        2: sp.record(
                            hash=sp.bytes(
                                "0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8"
                            ),
                            mmr_pos=15,
                        ),
                        3: sp.record(
                            hash=sp.bytes(
                                "0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795"
                            ),
                            mmr_pos=18,
                        ),
                        4: sp.record(
                            hash=sp.bytes(
                                "0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9"
                            ),
                            mmr_pos=22,
                        ),
                    }
                ),
                peak=14,
            )
        ),
        (
            sp.map(
                {
                    0: sp.record(
                        hash=sp.bytes(
                            "0x2b97a4b75a93aa1ac8581fac0f7d4ab42406569409a737bdf9de584903b372c5"
                        ),
                        mmr_pos=3,
                    ),
                    1: sp.record(
                        hash=sp.bytes(
                            "0xd279eb4bf22b2aeded31e65a126516215a9d93f83e3e425fdcd1a05ab347e535"
                        ),
                        mmr_pos=8,
                    ),
                }
            ),
            sp.map(
                {
                    0: sp.record(
                        hash=sp.bytes(
                            "0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8"
                        ),
                        mmr_pos=15,
                    ),
                    1: sp.record(
                        hash=sp.bytes(
                            "0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795"
                        ),
                        mmr_pos=18,
                    ),
                    2: sp.record(
                        hash=sp.bytes(
                            "0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9"
                        ),
                        mmr_pos=22,
                    ),
                }
            ),
        ),
    )

    scenario.verify(
        MultiProof.calculate_root(
            (
                sp.map(
                    {
                        0: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=1,
                                    hash=sp.bytes(
                                        "0x7463c9b814b5d9081938e21346fe8bf81a9a9a0dcfa7bcc03b644a361e395a3b"
                                    ),
                                ),
                            }
                        )
                    }
                ),
                sp.map(
                    {
                        0: sp.record(
                            mmr_pos=0,
                            hash=sp.bytes(
                                "0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9"
                            ),
                        ),
                    }
                ),
            )
        )
        == sp.bytes(
            "0xea5eb4c6212f178939883a6f804eef46074a83e4f258e072b600e9baf154864a"
        )
    )

    scenario.verify(
        MultiProof.calculate_root(
            (
                sp.map(
                    {
                        0: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=1,
                                    hash=sp.bytes(
                                        "0x754310be011a7a378b07fa7cbac39dbedcadf645c518ddec58deeaa8c29e0634"
                                    ),
                                ),
                                1: sp.record(
                                    mmr_pos=3,
                                    hash=sp.bytes(
                                        "0x06be3c46e5a06d7b3e438a9d698f4319dc628624a63e484d97f00b92d09edce7"
                                    ),
                                ),
                            }
                        ),
                        1: sp.map(),
                    }
                ),
                sp.map(
                    {
                        0: sp.record(
                            mmr_pos=0,
                            hash=sp.bytes(
                                "0x38e18ac9b4d78020e0f164d6da9ea61b962ab1975bcf6e8e80e9a9fc2ae509f8"
                            ),
                        ),
                        1: sp.record(
                            mmr_pos=2,
                            hash=sp.bytes(
                                "0x1a3930f70948f7eb1ceab07ecdb0967986091fd8b4b4f447406045431abd9795"
                            ),
                        ),
                    }
                ),
            )
        )
        == sp.bytes(
            "0xf0491ae550cf2109665e07df91118e03d4cf23c59b8b4a4dd8dff0726cc86ae8"
        )
    )

    calculate_peak_root_lambda = sp.build_lambda(
        lambda arg: MMR.calculate_peak_root(
            arg.one, Iterator.new(arg.two, arg.three), arg.four
        )
    )
    scenario.verify_equal(
        calculate_peak_root_lambda(
            sp.record(
                one=sp.map(
                    {
                        0: sp.record(
                            mmr_pos=22,
                            hash=sp.bytes(
                                "0xe54ccfb12a140c2dddb6cf78d1c6121610260412c66d00658ed1267863427ab9"
                            ),
                        ),
                    }
                ),
                two=6,
                three=sp.map(
                    {
                        0: sp.bytes(
                            "0xa4a7208a40e95acaf2fe1a3c675b1b5d8c341060e4f179b76ba79493582a95a6"
                        ),
                        1: sp.bytes(
                            "0x989a7025bda9312b19569d9e84e33a624e7fc007e54db23b6758d5f819647071"
                        ),
                        2: sp.bytes(
                            "0xfc5b56233029d71e7e9aff8e230ff491475dee2d8074b27d5fecf8f5154d7c8d"
                        ),
                        3: sp.bytes(
                            "0x37db026959b7bafb26c0d292ecd69c24df5eab845d9625ac5301324402938f25"
                        ),
                        4: sp.bytes(
                            "0x754310be011a7a378b07fa7cbac39dbedcadf645c518ddec58deeaa8c29e0634"
                        ),
                        5: sp.bytes(
                            "0x06be3c46e5a06d7b3e438a9d698f4319dc628624a63e484d97f00b92d09edce7"
                        ),
                        6: sp.bytes(
                            "0x7463c9b814b5d9081938e21346fe8bf81a9a9a0dcfa7bcc03b644a361e395a3b"
                        ),
                    }
                ),
                four=24,
            )
        ),
        sp.bytes("0xea5eb4c6212f178939883a6f804eef46074a83e4f258e072b600e9baf154864a"),
    )

    scenario.show(
        calculate_peak_root_lambda(
            sp.record(
                one=sp.map(
                    {
                        0: sp.record(
                            mmr_pos=94,
                            hash=sp.keccak(
                                sp.bytes("0x0507070030070701000000044e4f4f500a00000000")
                            ),
                        ),
                        1: sp.record(
                            mmr_pos=95,
                            hash=sp.keccak(
                                sp.bytes("0x0507070031070701000000044e4f4f500a00000000")
                            ),
                        ),
                        2: sp.record(
                            mmr_pos=97,
                            hash=sp.keccak(
                                sp.bytes("0x0507070032070701000000044e4f4f500a00000000")
                            ),
                        ),
                        3: sp.record(
                            mmr_pos=98,
                            hash=sp.keccak(
                                sp.bytes("0x0507070033070701000000044e4f4f500a00000000")
                            ),
                        ),
                    }
                ),
                two=0,
                three=sp.map(
                    {
                        0: sp.bytes(
                            "0xa2fd5ffd8bfb1936e8762e857b76572f14844aa377f13e211027d397237e84e9"
                        ),
                        1: sp.bytes(
                            "0x2510b9516b262cec8be88b0dee8a4f08a0c89060a5fcb859e6b119dedca7eeec"
                        ),
                    }
                ),
                four=100,
            )
        )
    )

    scenario.show(
        calculate_peak_root_lambda(
            sp.record(
                one=sp.map(
                    {
                        0: sp.record(
                            mmr_pos=0,
                            hash=sp.bytes(
                                "0x258ff0aa07802204fc15c478ff72d4f6caafdf31b05f814f4ec5106afa454a8e"
                            ),
                        ),
                        1: sp.record(
                            mmr_pos=1,
                            hash=sp.bytes(
                                "0xaca4581bffa87509b6557397f88cf5c2534cf900892729cd82aaf3cebe025fd6"
                            ),
                        ),
                    }
                ),
                two=0,
                three=sp.map(
                    {
                        0: sp.bytes(
                            "0x4f815ba60f512a92d199c973bcee1654860eddfe91c3fcc558275d3d4d58fea4"
                        ),
                    }
                ),
                four=6,
            )
        )
    )

    scenario.verify_equal(
        merge_sort(
            merge_maps(
                (
                    sp.map(
                        {
                            0: sp.record(
                                mmr_pos=1,
                                hash=sp.bytes(
                                    "0x1000000000000000000000000000000000000000000000000000000000000000"
                                ),
                            ),
                            1: sp.record(
                                mmr_pos=2,
                                hash=sp.bytes(
                                    "0x2000000000000000000000000000000000000000000000000000000000000000"
                                ),
                            ),
                        }
                    ),
                    sp.map(
                        {
                            0: sp.record(
                                mmr_pos=5,
                                hash=sp.bytes(
                                    "0x5000000000000000000000000000000000000000000000000000000000000000"
                                ),
                            ),
                            1: sp.record(
                                mmr_pos=3,
                                hash=sp.bytes(
                                    "0x3000000000000000000000000000000000000000000000000000000000000000"
                                ),
                            ),
                        }
                    ),
                )
            )
        ),
        sp.map(
            {
                0: sp.record(
                    mmr_pos=1,
                    hash=sp.bytes(
                        "0x1000000000000000000000000000000000000000000000000000000000000000"
                    ),
                ),
                1: sp.record(
                    mmr_pos=2,
                    hash=sp.bytes(
                        "0x2000000000000000000000000000000000000000000000000000000000000000"
                    ),
                ),
                2: sp.record(
                    mmr_pos=3,
                    hash=sp.bytes(
                        "0x3000000000000000000000000000000000000000000000000000000000000000"
                    ),
                ),
                3: sp.record(
                    mmr_pos=5,
                    hash=sp.bytes(
                        "0x5000000000000000000000000000000000000000000000000000000000000000"
                    ),
                ),
            }
        ),
    )
    scenario.show(
        MultiProof.calculate_root(
            (
                sp.map(
                    {
                        0: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=3,
                                    hash=sp.bytes(
                                        "0x065aff9602a25b0538643a8a81fa29fdaba2ae568b61ac217cea9233798ab14a"
                                    ),
                                ),
                            }
                        ),
                        1: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=0,
                                    hash=sp.bytes(
                                        "0x95e6f12aa5a8a8f4c4910166152849834cc388a8151c43298b99af0de7125e99"
                                    ),
                                ),
                            }
                        ),
                        2: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=1,
                                    hash=sp.bytes(
                                        "0xe43a34012e0a45ce6075ac377bf0a35ba316c9f324cafb9016e0e58032c01ec8"
                                    ),
                                ),
                            }
                        ),
                        3: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=1,
                                    hash=sp.bytes(
                                        "0xd21d5d4bde2d68d4179093c889138cefca3eb4e95e91554876153832848c8887"
                                    ),
                                ),
                            }
                        ),
                        4: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=1,
                                    hash=sp.bytes(
                                        "0x427e513e4be7a3b801b69ac49ffbd435a0e46114e2ab5e1258518017d4a6c595"
                                    ),
                                ),
                            }
                        ),
                        5: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=1,
                                    hash=sp.bytes(
                                        "0x7da58cfe1038b71aeef0b0f22ecaea7d6368916f5214a18fd971bd34c6ab86b1"
                                    ),
                                ),
                            }
                        ),
                        6: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=1,
                                    hash=sp.bytes(
                                        "0x479f391367a51f2b8f14ee907ebd21e3c7d1da2ea63946335e4ed13e4e882e23"
                                    ),
                                ),
                            }
                        ),
                        7: sp.map(
                            {
                                0: sp.record(
                                    mmr_pos=1,
                                    hash=sp.bytes(
                                        "0x469d3885ec0cae3f1172312460226cfbc0a4140230f8761d0fb6bde6d83d8408"
                                    ),
                                )
                            }
                        ),
                    }
                ),
                sp.map(
                    {
                        0: sp.record(
                            mmr_pos=2,
                            hash=sp.bytes(
                                "0x0302a35dfed8f03aa94acf2a4e0f01909591e0e39baeacb2ba5fc9ab83a514ff"
                            ),
                        ),
                    }
                ),
            )
        )
    )

    scenario.verify(
        c1.verify_proof(
            sp.record(
                snapshot=2,
                proof=[
                    sp.bytes(
                        "0x53db3d426fa99eff2cc6ef1f07a226c2e5b32d9ccc2b67411d52e8d2b0de8d13"
                    ),
                    sp.bytes(
                        "0xbca5ce83486f6bd8be90523d0e9bcefd812fbd451337b584d32f8203dbf340c7"
                    ),
                ],
                leaves=[
                    sp.record(
                        mmr_pos=8,
                        hash=sp.keccak(
                            sp.bytes(
                                "0x05070700050707010000000641535349474e0a000000460507070a000000100000000000000000000000000000000502000000290a00000024747a316834457347756e48325565315432754e73386d664b5a38585a6f516a693348634b"
                            )
                        ),
                    ),
                    sp.record(
                        mmr_pos=10,
                        hash=sp.keccak(
                            sp.bytes(
                                "0x05070700060707010000000641535349474e0a000000460507070a000000100000000000000000000000000000000602000000290a00000024747a316834457347756e48325565315432754e73386d664b5a38585a6f516a693348634b"
                            )
                        ),
                    ),
                ],
                mmr_size=11,
            )
        )
        == True
    )

    scenario.verify(
        c1.verify_proof(
            sp.record(
                snapshot=4,
                proof=[
                    sp.bytes(
                        "0x93a2f7fc624f598296a71ab13f1d1df71490fe42f2781e25f838023df0de8f88"
                    )
                ],
                leaves=[
                    sp.record(
                        mmr_pos=1,
                        hash=sp.keccak(
                            sp.bytes(
                                "0x05070700010707010000001441535349474e5f4a4f425f50524f434553534f520a0000002005070700020a0000001600020a3b823f37878cbd11aed15191d33a8c8137340b"
                            )
                        ),
                    ),
                ],
                mmr_size=3,
            )
        )
        == True
    )

    scenario.verify(
        c1.verify_proof(
            sp.record(
                snapshot=5,
                proof=[
                    sp.bytes(
                        "0xa2fd5ffd8bfb1936e8762e857b76572f14844aa377f13e211027d397237e84e9"
                    ),
                    sp.bytes(
                        "0x2510b9516b262cec8be88b0dee8a4f08a0c89060a5fcb859e6b119dedca7eeec"
                    ),
                ],
                leaves=[
                    sp.record(
                        mmr_pos=94,
                        hash=sp.keccak(
                            sp.bytes("0x0507070030070701000000044e4f4f500a00000000")
                        ),
                    ),
                    sp.record(
                        mmr_pos=95,
                        hash=sp.keccak(
                            sp.bytes("0x0507070031070701000000044e4f4f500a00000000")
                        ),
                    ),
                    sp.record(
                        mmr_pos=97,
                        hash=sp.keccak(
                            sp.bytes("0x0507070032070701000000044e4f4f500a00000000")
                        ),
                    ),
                    sp.record(
                        mmr_pos=98,
                        hash=sp.keccak(
                            sp.bytes("0x0507070033070701000000044e4f4f500a00000000")
                        ),
                    ),
                    sp.record(
                        mmr_pos=101,
                        hash=sp.keccak(
                            sp.bytes("0x0507070034070701000000044e4f4f500a00000000")
                        ),
                    ),
                    sp.record(
                        mmr_pos=102,
                        hash=sp.keccak(
                            sp.bytes("0x0507070035070701000000044e4f4f500a00000000")
                        ),
                    ),
                ],
                mmr_size=104,
            )
        )
        == True
    )

    scenario.verify(
            c1.verify_proof(
                sp.record(
                    snapshot=6,
                    proof=[
                        sp.bytes(
                            "0xf805950edaf6f0ee75cf7ba469c2ea381667f1b75d5bfacf1749500448019049"
                        )
                    ],
                    leaves=[
                        sp.record(
                            mmr_pos=3,
                            hash=sp.keccak(
                                sp.bytes("0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000ff000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000")
                            ),
                        ),
                    ],
                    mmr_size=4,
                )
            )
            == True
        )
