import smartpy as sp

from contracts.tezos.IBCF_Eth_Validator import IBCF_Eth_Validator
from contracts.tezos.blueprints.IBCF_Crowdfunding import IBCF_Crowdfunding
from contracts.tezos.libs.utils import RLP

# There values can be generated with "scripts/validate_eth_proof.js"
BLOCK_NUMBER = 8370810
BLOCK_ROOT_STATE = sp.bytes(
    "0x213f6a9701973e267dd0bdabec9bdac0a346ef010cb12c763f1f3eec0a60c357"
)
EVM_ADDRESS = sp.bytes("0x91fb7A14C4100a6d7eA391D5DB82a1E6adE6B471")
ACCOUNT_PROOF = sp.bytes(
    "0xf90c01f90211a01902b247bfd2b0706f2f46cb6aa131536ebd86d713a3a5e0d21cfc798add7797a0ba4742ab372a880c41ead9bba17c8ff7d8002f97b5d5fb0fca2c0229de0a57b3a02b08b7a2cc266591b2a7a273fe344b630e85922cb412af3a21e54bf89faf74b1a049d2feba3ec91dac3f89015dbacbabc1445636a2f0c58c15e23d4debf90d2ab8a06a85de0f9e2e605d7a5695be5fd99862d3365269883677485dfc671b0c7a351da0ffd453e390fa89d1e3bbf7f0c0e4d839e72ca89bb6f15adb5537623496f3cc0da09b4ef2dbc04b6acba7ac615c10ccf0f7b764d8d77364b7b9cecafb4543358d55a0a8459e203eb80fae24413dc2247780c77305b6780a83a2250ff4231da31ffe08a00ff7368436b0eb58d78b221ac4f2dbda035a3023f8d89c690144386744f5c502a0677a954136a7797d4ca419dc097a135f771c8f2e8c42b2a2a33515529c0280eca0d5ab72499744e54c8decb98fe31deea80a99b4ba46210825361636e70b03bbf1a04a03b0947d1a6d3676d44fb5dfc911d65304fc0b95a3d3fe11c937849e41741ca0fd096d1808b9392f8b57d531f3b0ca4e1da2c7ae49a362b2a102fc0426de5088a0021b7fe7e2d79122c38881f974c30b9d65c7e23f5d05bdb617a41936eacc3c04a0f77f0f7336314d212f96c3a290c73c4c84b1daf68a86650a741286f710006369a06df12bb8b84046a52da4234cc9ccddf5bf18576b7f6ed60122fb47fd73bee68380f90211a0af4d0eef7797eca6e17b575e1d37e415d5f22baaa56ea8fe0e9abae8af5bbfe5a00c55eea34e4662dc711cff54da303548ddd95dfba4c793d71f118a3e3ffda127a05b788a9e78ef874c417d5c619d243658f29fa282774229997ff4081aa805ffb3a037bd3b52070861f5ab253cd824e6a9b1b91c967911dfbc398b97d445adce75b7a0875e22ccf5be160ae37fc9f52a115ee0da1021b84d5bec0901d9b231477b0c40a03a23e95ad892b43b854c57abfc7369bbb4d5aac864db25fc8291d8e701531726a0fa8c26fba3f8d680627dcd23631dfd56c9dd48b2f542bd6e616d9cb0e590c96ca0373c191e7d6d892a309445fb10bb46608a4e8bb70b14334aa65ef70d12d535c5a042b8efd89dd50d1328748049c83ca1bdd8bd10f82b08a534e657c49e52a5771ea0a63d4cc00220c7a5ba43b71141f88281d99c223140b7207b57ba672519ed74dfa098fef7c4352cbc0afed61108b5468b20dc335f6064689a7be24ad62a41c468ada0abdd62692343025d653e0be856aab0a3e6ced4e8470be8372164dd9c9b733bc6a07ed3de8886920e94ffefb0ec17c38ca1c42c565038c57ada440f7f5bb0ecb2eea0887db901d9cf407308fd82faff21c5667789bf542a9da103930e8b6511eda9e1a036c3c61c7ddf7892752ed017778d00dfba436b49b304d8c271251bd96c9acee0a07e29aea022bdd9be41bca4f101679d4bac4b511b3d0ff5b5abcf76c14be3927b80f90211a0dae665136640b53d0c160483144d247a1a3a153b09dde05c63e033216b50d1b8a080c093a84d60350fdfd1b9905e11a9488b017c4fdd55404bdd174999b5eb9d51a0a14a90cfb08f86a3fcd18756e3761ff6362d689fb341de66cd6799d3c6901cada0e4eab45427ce28884dcf8386066327d516cac880d4fac2f1c28135d35b055604a0eb1b5ba75d69267216db6e390a7a7210009efcd98838e4f4626e6603c4d5bacaa0413ebf1f163d7a0112055a4ab3a596450ec026e34e070e5d980456fbbd343d8ca0ab24c2a4dfc5123f6ed0ccd8db6801b3bba28a9098c4d8a9f067bdd7bfa54a8da0e3331b612db5ee0a8d304161bda1904b127d584c7eab68d06e5eb271748e3975a000cb5c8dcf3d05fc30c41740d0878536ca164095fce5c46f1384ffcefa8ddd0da03204c54900d6cf8a323df3429fea4115faceef7255f0354a958bb43af1cbd0a0a0e5d0ea7a13d62f0fb8dd7aceab262b31c5401950a548c60e6cae64138ba1a406a0ee3e93f2eba4556fad0c9a63ecea411df6c7fa07566b26780399fc6bbc34ade1a057aad2baf0347ef32d7aed0cec6f20e5827e8420adea8f2e861f4ef7d2f54291a09914fee60b34bf82842468403281f66cc58fbfccc09df731480908f523563769a03a2519733bfc02f08bbc034187898acecaa953ca46213323e7de77aab374b22ea033d6f223f7baac21cf27eb2c627eda1695b5b348377eab4e06e8fc7d6f6b3fc580f90211a028e0c3f76ee6b065b52e475a7f9761594eeb4ba1dd4f97708bd1c86aa7f592c7a0939f11951a16d0460a9b5d989a4de04f83720000cf485b22ed500b6a2b4d0c17a0a1e7d8ebc8b3cb9c41ecfe90839a7e2f34501a007ac7200e1bbc19aa5e0e75b3a05dc7f2b45fdcb904943d610301f5e2788c46103d2a904cecfffc3f417a487fc0a0660a5b5ec297d4538035fd42acfcfe59ef6932c43bbf22426e76e0e2fad30c03a0958f3279eacf2718b8356c1300c14ccf2901be6072ee561b53596426b103bf10a04d270a4585d7022ab7e538bef96ff1ba394be6124b8410a7e986f66f006425a1a00d3068798a4c09fbbbd3e63ee13204b703b83278b25e7d9be4fb9078baa49fe3a07c1a532579db9ec5858c36854e6c056b205af353ffd6496ba3a2f27b126c53a1a0f0b3266592a688b6213d4d7dd5906fd3e413e05baea6affd12f5000fd59de83ea07c5ed21b05346a2dcde777ad649b687ae435d4337c18c77ad2be1f7fbb817de2a027b5af0d6d314bd94b2e1813d1a22025f2a63d990402555f38513e530a74130fa09aa6f94ba5cc522f1b1ffb7fc62456f40141668392276a00f63837dd9935df7fa045f9b54b9d711b47df7fed2810e1749898966fc6f3c640e428443d525e34a74fa0c7854a62c518e0c00c28de173c9157b322106442e63235f9fb2aa0b5867c5524a0ce4928c26abd560efaae6b500c6b45d7b55d15be017795fec8b114fe34af78a980f90211a06d39028e59ed6344e46585a6c9b82accd52852d777dd8ec9b70c00955cd48ceea010d04b5a1ddbab4b94e2834725457e1a5faa0819f6acdef80b0e388a983ba00aa0102d9070d94558d1baeedeeb3af6d4f83bb2c3de2ebf11ce2f5f63b07c0744fea0b9f0f7179e4e88d8e30a4e2815c6b454337a2087b7c18c77d04eeee36262649ba02e6e33cd87f7b7230251401109fb33ab113f8f37ee8b67f355952df7e5e7ba9aa07d414dcd781404b37e67dbe29e6bc81eecbab05126bdbedd400b2b4c699739a8a0f76191d1ad369325961f895728bb479070342224ece3ba1efb8246a393720acba053efd6415db33c5eecfe5f7f41e6d4908db5473303a7f7b80bda444056e2666aa048d854f77cbc5a0742f491b0181e73ae94c99c3fe190d861b5187c0254b72705a0ca0659af3651f816d38b2c90f3afd0fb1b20986a5001976ec2f1909a93870164a042e78dbd70ec44a71ddc8d70f9dca5766549fc6681f4e8a0314f7df657c970faa0addcbffbf920e7e67a9f33755fc41509f4157ddfe64de133a51b1b464586585ba0d8d7ecd316fe3bb128a2c746d0842b345e8087490565ae77e3a7a24a24ee1aada0ea125f8961298ca667f0c05d8f833c28b5b6a376925794026bcb49c1de8e634ea088d9dace3271a9acbdd1044fd39b22c552b2bfb8f892920b55edde5e0aeda0e7a052223e52be9ca6ec22af833e0b1a91f51f108da9abe75fb99705c33861a613f580f90131a064f2fd28e517827a52cbb740b526e35e64b0a85d780f2ccb67e0b598531596668080a05b3d370e7d0576d3f2efaf27a8707dd89b731013e4d9670b2bb9a069c49165e8a037f877d28a3e1053b42b0435c6e0420a61b37097143de22bce486e0559c3a4278080a0a1941febfb2402f5eb0e7bf5271758b5cc7867fead5bcd8fb79543d5365eedf68080a0477737c078ca6ef13b34940a053b496248db0ff27c19095709a2d961f222c87ba038ddad36de8c9d825b849b0840894d5237d6400d80d4d501ceeb23bc5bbef291a09cc408ec7df853abd357c2188ad0b5537a51924d978c7172e0081ae3122e6e63a01541dbfb6bcde02d2b85039bd3dbbfef4e9cb164d6cfd27131ad90b95a3acd5780a0894c0a0048d7411cb1500f55547d00819dc8a1c95510610d913c9aef2e9836ea80f8679e20740f55f06cfa54bf5fd7b66119758afdc9054d4e7f710495d353513721b846f8440180a0d934d046055c17df203a762c73e089a5aaab4f093d00ae7d5fb9f74fe0a87c90a0ab9d2990f76301bb69ecc6ea188ee7fd186e107d0a6c08b685403d26551f87d6"
)
FUNDER_PROOF = sp.bytes(
    "0xf8ebf8b180a00d24d9b786bfb5f20e3e27e4a821dbe48ba8fb9d9d6070a9eebe63fa98591005a03e2a97c8976155ebb2812181977aa430da1df1035ec8d417fc6f69462f7c0cbe80808080a0210a78628487fba0e4fb33e7576903f7a71463af05bbb804a6e0dab1998f3fc2808080a0236e8f61ecde6abfebc6c529441f782f62469d8a2cc47b7aace2c136bd3b1ff080a07d9d9e372c59e462c32bce5ffd42c5a2e0aee06f642ada81888f8a014fac872c808080f7a03fef4bf8f63cf9dd467136c679c02b5c17fcf6322d9562512bf5eb952cf7cc539594f7498512502f90aa1ff299b93927417461ec7bd5"
)
AMOUNT_PROOF = sp.bytes(
    "0xf90129f8b180a00d24d9b786bfb5f20e3e27e4a821dbe48ba8fb9d9d6070a9eebe63fa98591005a03e2a97c8976155ebb2812181977aa430da1df1035ec8d417fc6f69462f7c0cbe80808080a0210a78628487fba0e4fb33e7576903f7a71463af05bbb804a6e0dab1998f3fc2808080a0236e8f61ecde6abfebc6c529441f782f62469d8a2cc47b7aace2c136bd3b1ff080a07d9d9e372c59e462c32bce5ffd42c5a2e0aee06f642ada81888f8a014fac872c808080f851808080808080808080a08afba6aed49a21040ee266fe274dfdd29da82b041d2215a563bcf08420434edb8080a0b28385cbb32330e8f1618d19ad7404342da35ee1e332158edae8e54730e23c2380808080e2a020644dcf44e265ba93879b2da89e1b16ab48fc5eb8e31bc16b0612d6da8463f16f"
)


def get_nonce(n):
    return sp.bytes("0x{:0>64}".format(hex(n)[2:]))


@sp.add_test(name="IBCF_Crowdfunding")
def test():
    scenario = sp.test_scenario()

    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")

    validator = IBCF_Eth_Validator()
    validator.update_initial_storage(
        config=sp.record(
            administrator=admin.address,
            validators=sp.set([alice.address, bob.address]),
            minimum_endorsements=2,
            history_length=5,
            snapshot_interval=5,
        ),
        current_snapshot=0,
        state_root=sp.big_map(),
        history=sp.set(),
    )
    scenario += validator

    crowdfunding = IBCF_Crowdfunding()
    crowdfunding.update_initial_storage(
        sp.record(
            ibcf=sp.record(
                nonce=sp.big_map(),
                proof_validator=validator.address,
                evm_address=EVM_ADDRESS,
            ),
            recipient=admin.address,
            tezos_funding=sp.map(),
            eth_funding=sp.map(),
        )
    )
    scenario += crowdfunding

    scenario.verify(~crowdfunding.data.tezos_funding.contains(alice.address))

    crowdfunding.default().run(sender=alice, amount=sp.tez(10))
    scenario.verify(crowdfunding.data.tezos_funding[alice.address] == sp.tez(10))

    crowdfunding.default().run(sender=alice, amount=sp.tez(1))
    scenario.verify(crowdfunding.data.tezos_funding[alice.address] == sp.tez(11))

    # Submit account proof for a given block (validator: alice)
    validator.submit_block_state_root(
        block_number=BLOCK_NUMBER,
        state_root=BLOCK_ROOT_STATE,
    ).run(sender=alice.address)

    # Submit account proof for a given block (validator: bob)
    validator.submit_block_state_root(
        block_number=BLOCK_NUMBER,
        state_root=BLOCK_ROOT_STATE,
    ).run(sender=bob.address)

    # Invalid

    crowdfunding.funding_from_eth(
        sp.record(
            block_number=BLOCK_NUMBER,
            nonce=1,
            account_proof_rlp=ACCOUNT_PROOF + sp.bytes("0x00"),
            funder_proof_rlp=FUNDER_PROOF,
            amount_proof_rlp=AMOUNT_PROOF,
        )
    ).run(valid=False, exception="INVALID_NODE")

    crowdfunding.funding_from_eth(
        sp.record(
            block_number=BLOCK_NUMBER,
            nonce=1,
            account_proof_rlp=ACCOUNT_PROOF,
            funder_proof_rlp=FUNDER_PROOF + sp.bytes("0x00"),
            amount_proof_rlp=AMOUNT_PROOF,
        )
    ).run(valid=False, exception="INVALID_NODE")

    crowdfunding.funding_from_eth(
        sp.record(
            block_number=BLOCK_NUMBER,
            nonce=1,
            account_proof_rlp=ACCOUNT_PROOF,
            funder_proof_rlp=FUNDER_PROOF,
            amount_proof_rlp=AMOUNT_PROOF + sp.bytes("0x00"),
        )
    ).run(valid=False, exception="INVALID_NODE")

    # Valid

    crowdfunding.funding_from_eth(
        sp.record(
            block_number=BLOCK_NUMBER,
            nonce=1,
            account_proof_rlp=ACCOUNT_PROOF,
            funder_proof_rlp=FUNDER_PROOF,
            amount_proof_rlp=AMOUNT_PROOF,
        )
    )
    scenario.verify(
        crowdfunding.data.eth_funding[
            sp.bytes("0xf7498512502f90aa1ff299b93927417461ec7bd5")
        ]
        == 111
    )
