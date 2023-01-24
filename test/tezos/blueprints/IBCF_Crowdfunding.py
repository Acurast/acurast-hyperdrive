import smartpy as sp

from contracts.tezos.IBCF_Eth_Validator import IBCF_Eth_Validator
from contracts.tezos.blueprints.IBCF_Crowdfunding import IBCF_Crowdfunding
from contracts.tezos.libs.utils import RLP

# There values can be generated with "scripts/validate_eth_proof.js"
BLOCK_NUMBER = 8368135
BLOCK_ROOT_STATE = sp.bytes(
    "0x0ee04963a093c360174e4cc52090ce2f0e3baae054fd72d8f82dfc936ef54150"
)
EVM_ADDRESS = sp.bytes("0xf685C24079B7342261075a651ba677cdc5458852")
ACCOUNT_PROOF = sp.bytes(
    "0xf90c56f90211a03698ed64ee0c68c74070d31a163222e3ff73da1663885e6376c2e26dbebde380a0cc753e2d11a0fd733b07075eb538906a01f44fb4470fb9e52867da1226deefcfa07a618437b49bc7e986c72bc7089b9396c6e3268cf0f5ff1945f3d5747b3541b5a077bf5d07dedb31618a660887d0df79debb10c1303a6a1d030f67e70b1f31c6bfa0e7caa29cbe4fe5ba0e593093dec4e22eaf2f92b562b9d53bf9ebcf4946c1ae22a0dd8500bad31d4ec37a7e0a6f0c473a7a99a8465b6e29408624a80f78e3e8f115a0ecc43aacaa7ec101e65242d712b5eded6d3a77af21b6fbae143f5ca7b5220518a0fbbd5640cf0e23d5207c27525cc5296035f73ff6203ce9515cf7bb3d4ec59540a01980669a89c30182e75db91bd89728a3875497fe8c120c5b5bc9996e6880b62aa05642fae4655960c4e65467d277839b7a2f8a425f97bec01d554a090d8ee3ac92a0ce8175d189bf414acc1cfd1140f5a49c4cd3e95f013248d8644d813cc757a9faa0b58fb80d9f5b965d6014f76c88748258bff2b916b456b572ee013db1aea64a6ba0d2dedf345151ed70ad7fc5d238c7149a6cf21188eb348887c804838188a3ba06a0131fc765a7605f1b170a51fc25b1853bcf6caabe10660ec650841340ca1c5d7fa09db8387d5e42327f6440951aec107b73c11644b29c89189fd6fad8da007039aaa0378aee78aa47be92ebcb1ce1e058a41632190412ac753df0db7612ef1215cb3f80f90211a0fe6049be027247ced39727098881b60c6901b77985ca5dee1157e29f380c6390a0f614c2af98d3754f20bf9a5c6b53ec9352798447aa505ef17417e585d47621b2a0a5c6609d3c7920172628c131497127b0cecd19cdf2b700dd8de81a80767e111fa097cd25c6f484ff6204cb2447e0cd9ca005022e02b6da33193e61e5c56289aecfa0d7f6d8f2cd50a0898a62a566f25b6f36e805e541809bc8615ff8efaa3c6e5094a0e3c0a8f49295d99196b9f3a85a3570118cac5d94c08e6a2d362acb7cc3565654a0bf4fa0a38e4b931d433753eb5a1a6990313f79f07f6bd3345e0986d188895148a074a77ff048b1d4ab6a518ea04a742f8d0bf6fefbf361db541e60dc087dd26978a0c57006aa5821b5e7e1e0e757a2e4dcb570a0beee37d06b4974fcec455ea630a4a02d3039d40d394d93aa8e188073d5f3851a4a6735cdff3d002f9437be4287cdc6a00891a8043154462d6860d6634f310adcb05755678542bee6d40b628c3a196f09a02be33f6d3c105acc5f4292a152eb6b6bc5b1be31b02714c38842ae2a8e56430ea0dc15307d7daec7c15cc88126163536ee02dd35706061ab430c204c61fd04140aa05e27e474f6c83093e7306632a6240e3eacd2bf55166b669a9f0ac23861f4c8c3a08163d583be23f31feea60aa163e96574f60c8e53b3626567c27b280263f0e3c4a0cf0491ebb59356cbdb41b45e457c634920d05f428fe56074cdf0a4806aafaad580f90211a04c20aefa0f4e2e8ec9aa47a1e9d33b676a411034618ee501a500f41f01abea13a0288fc76bbf58076eba712fad002d038ee8a9b69bd7806fc8da72bbe4f57bad18a029408eec46dc850a47f8dd6b1d93e12f7b3682aeb6eac5a08bc22960923b0f89a04e6f77e5bccf3f970046be78f404bb5bf02bb70dad3b02297a8759e6efdc8bdda0ddcd971eda84dbb9588d0652e970556fcf8212dd13a1633e5c1d71e851a6aa43a01211f82db0e43f7f5dcbedfedb5aa41f27feb3298603812ee332081fb286a166a03c3f12385159554df86f71b7856027086ded313dbb68a6ab760492a7c8bed5eda0232558c37e8fa2cd53556648b9a27e2f55f7834382cc368a8aad81df0aab7648a0fca31d71be26aba3311f014d1f1c1608251dc5dd599c0795bd632f40d726a038a0fec56f98666483ec01462bdcc7a8a4a10475b71115e21cb392742ceedbd44ae6a0051efff1d393391995d0dd0fe9ec059a8c54c2f7e524816fe5b0d8240a137fa8a062b766cce6b798a9de2a5f419604f10a5abc8360eafbc05183a1fa512546037fa0b27b3f82ab17094fcf504bf1243c7d2af9619b23f3a5412d1eafeba4e060e621a0107b13e40928e015c77add0f650a565f1bd19c76786d4bb17a52b06f63804edaa0b541be2d7146e5ceaf28967a2a5719f3a011bc56204274663d794d974bb78d4aa01d8b00f677e3741500a69c5e84b8f3792c071bd10ce06be52c2148156e93d33e80f90211a0e5673459932f821caf845db4afc846b420be1da480a7af6fa70e76d3b672158da0174e70861b188faf181fd483f387558883a1dd5023ccaa108dc0da8ae9af886ca0ce847f4906ac7e5264a6d1e1233fa0867299d92a23f8407370e24426e5e9f263a0a31f144cd0c44dec1d52dd1fc3b0978892e1ee47e25f54665efc5b1a61dddb60a04ab1bea8e50fda92292202e1ad18eddbcb719936a147d31bfb453c180f7b8eb1a0c5b4e9270c22abde8ac7ca7f68d3db9ae9bb85656bfce9b89544d18e3f84bdc4a00bb2dd1a5b16160c05f2f4dec0362509d5138dc3dfbadc9161907a54de65ce28a008a8217867a01b1a7366ab46b2aebd5705910ff652253aba82476c05cc0768b5a0c729d5cfa4fd78e2cf05b652fbbafd6db2b438d5bfd0a9aa51988db180a5bbbba0faeae83626d558e82d0d5d5ef2c17081ae763af7caf59ae9ea87a923adb89fb3a05e26d97895e75d3178318fdf9ee0c2773149586b25cc87c100c7e3eaa0947502a063fe377de3fe1c54d4c79d529c4a2e7efd1719ca64963e2caf61349578f405ada0160ecde71e547925a12c916732884f7f36579de0dbfd4850d56d2ac835e49247a03f4b08b08509941f2492c3d2b4fbf9b2784da01637a6138cbca1dc56887494f0a08aa9e17634fcc5a190a1777513af90427f2f9a3873fda33c33a7a2eab85ea837a007723eda3e18711d1e148ebeb4dd67bc11bcc44a541a9a44d0d6df83e0f2ee8180f90211a0c9826b537c9cc813967e53ad5e98e1c06c2f60899af2aa191fed5718bc1c04eaa0e7795421df5fc7fe9cb2cba84ce874597a181642540c9716e8d998d3e51e3882a0ed56dfa891f75b9998df69ff2fb21601bb7b98db85189d8c043b97e3916a7a07a00e10ffe101d09055ca5618ef7af1e3cefb334d7669254d039bd4523935c49265a0c40024e96733bd3bab4d408fff972aec7dc64a673c459c7d2ce999d60643a55fa0ee188026ee5064ac841fd7294c82c749a86625858b26a45a4d7be56607f6db04a0a93c4e070cb6018fcd3cfc4a116d97be8af5ab87005081420a52e887b710eeaca0ef66113bf6080b81e8e58938c167602df3c30f294740d86e06d81e0c19b38c1da0fdecfa23ad2b9036c7fa450ab7d52f842ea4be65dcf6ac58deef3103a6a21ca5a026e5b054bb2b95f56037a34b00d8f3d7527ff9a16b1004e9053260fe08daac8ea0f9eff1545b53e45cee8d03a1847614647eec77f3e8b223d8ed00e68dd843478fa050c0e12608b1702ebddec0e6ccfa0289932f7b73f7b1e17914daad4003b6cf6fa0a83180927f91921b732ecbd7f93554b54376a4eaafb49b0512d385637dbeb1cba0887787f13e7343f377654f88bbaf36a666e1ca9cac5a82b4563d47cd481e12d8a088e0a9e63746adf47d2c68db08dc11c3886aa6105c7cd94cc1c6882d665bf79ba08e77f97dfa466b44f1564f46ee532a6394d910f079fb1e829a98b339fc1e1cd180f90111a08a8562ea6d8816b27d6bdfdcf6a30b414d44decd3b567da6bed63af2074a44c880a033dd46b31a1cf8b270adaa423ff8cb9fd4d4c9ed412906c789d81e584176adab808080a03e25d465fcb8475873dbe6a68ab8198cfdd8a1c3ea2cf273c702c56d0a2328c280a0c47a4634ebbee7127cea65a8a640e49f611e8f82e9449f368c01dcf251cb00b5808080a0e83f472bb1b7014cf5d1cd93d605cd04a3eb473bcb4b98bdc3ca5fc0a3c7135ca04c5e09937d7f6bbf98cc956b2d76c49b2b0246d7d26650e8883cfcee086e129aa0c8059909f32554dc3002dded674416de4738fa57bffd3eb1b867a87842c9dc38a07ecb5b7d1f669febcfda7db57b6f34774b030bff054b4afcec5a099326003b4980e217a0eca1792870a2b4b9e5cee5b215c961fdf0f646ec3568db85de2a3f4953edb654f85180808080a00c22e74ff46ba7fab7bb8e8f3020511e1611627f73aee8f5e4ed36fbd721d4858080a0176e7a09919b9f4e818c56172a9aa8b4ea8a0f87013775bb6badfb82cdbfefc8808080808080808080f8669d200da9d8de5784e1b0c416b09f96884252f0311b561e13696423427f5db846f8440103a0def00e1f5c8dc75b935f8ce2e698c6fbfa0c2b17be4341c172a219d9d302a8b5a03367fecc9f2d21de21eccc03b63fe4b0ad3497445ab038bbb93e0e3efd71e3cd"
)
FUNDER_PROOF = sp.bytes(
    "0xf8ebf8b18080a04e918b76be51be2f02df0ac6191ec2765d401d2229e47291806815da755f5b5e808080a05a2502c5a4f4f5a8b535353dcfd6bcf63bb034391e908a9f53d7b9dd1b7b626ca04e3050077deebb2f8b239c30869ee4fc8003c5b3a6ef83a2e5cdfe9b48b88cd380a0e39b834934e2a4395b279c598cb66b02d8b26a44207bca0bda8d6d1f66fc328c808080a06c9563879bcf8bb1869f11eacc4698473aa7006badf1ed3a1578500a7d34b45f808080f7a036b32740ad8041bcc3b909c72d7e1afe60094ec55e3cde329b4b3a28501d826c9594f7498512502f90aa1ff299b93927417461ec7bd5"
)
AMOUNT_PROOF = sp.bytes(
    "0xf8d6f8b18080a04e918b76be51be2f02df0ac6191ec2765d401d2229e47291806815da755f5b5e808080a05a2502c5a4f4f5a8b535353dcfd6bcf63bb034391e908a9f53d7b9dd1b7b626ca04e3050077deebb2f8b239c30869ee4fc8003c5b3a6ef83a2e5cdfe9b48b88cd380a0e39b834934e2a4395b279c598cb66b02d8b26a44207bca0bda8d6d1f66fc328c808080a06c9563879bcf8bb1869f11eacc4698473aa7006badf1ed3a1578500a7d34b45f808080e2a03fef4bf8f63cf9dd467136c679c02b5c17fcf6322d9562512bf5eb952cf7cc5301"
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
        == 1
    )
