import smartpy as sp


from contracts.tezos.utils.utils import RLP


@sp.add_test(name="RLP_Encoder")
def test_encoder():
    scenario = sp.test_scenario()

    # Test lambdas
    scenario.verify(
        sp.build_lambda(RLP.Encoder.encode_length)((1, RLP.STRING_SHORT_START))
        == sp.bytes("0x81")
    )
    scenario.verify(
        sp.build_lambda(RLP.Encoder.with_length_prefix)(sp.bytes("0xffff"))
        == sp.bytes("0x82ffff")
    )
    scenario.verify(sp.build_lambda(RLP.Encoder.encode_nat)(0) == sp.bytes("0x00"))
    scenario.show(sp.build_lambda(RLP.Encoder.encode_nat)(0))
    scenario.verify(sp.build_lambda(RLP.Encoder.encode_nat)(127) == sp.bytes("0x7f"))
    scenario.verify(sp.build_lambda(RLP.Encoder.encode_nat)(128) == sp.bytes("0x8180"))
    scenario.verify(
        sp.build_lambda(RLP.Encoder.encode_nat)(999999999999999)
        == sp.bytes("0x87038d7ea4c67fff")
    )
    scenario.verify(sp.build_lambda(RLP.Encoder.encode_string)("") == sp.bytes("0x80"))
    scenario.verify(
        sp.build_lambda(RLP.Encoder.encode_string)("TEXT") == sp.bytes("0x8454455854")
    )
    scenario.verify(
        sp.build_lambda(RLP.Encoder.encode_list)(
            [sp.bytes("0x87038d7ea4c67fff"), sp.bytes("0x82ffff")]
        )
        == sp.bytes("0xcb87038d7ea4c67fff82ffff")
    )


@sp.add_test(name="RLP_Decoder")
def test_decoder():
    scenario = sp.test_scenario()

    # Test lambdas
    scenario.verify(
        sp.build_lambda(RLP.Decoder.length)(sp.bytes("0xcb87038d7ea4c67fff82ffff"))
        == 12
    )
    scenario.verify(
        sp.build_lambda(RLP.Decoder.without_length_prefix)(sp.bytes("0x82ffff"))
        == sp.bytes("0xffff")
    )
    scenario.verify(sp.build_lambda(RLP.Decoder.decode_nat)(sp.bytes("0x00")) == 0)
    scenario.verify(sp.build_lambda(RLP.Decoder.decode_nat)(sp.bytes("0x80")) == 0)
    scenario.verify(sp.build_lambda(RLP.Decoder.decode_nat)(sp.bytes("0x7f")) == 127)
    scenario.verify(sp.build_lambda(RLP.Decoder.decode_nat)(sp.bytes("0x8180")) == 128)
    scenario.verify(
        sp.build_lambda(RLP.Decoder.decode_nat)(sp.bytes("0x87038d7ea4c67fff"))
        == 999999999999999
    )
    scenario.verify(sp.build_lambda(RLP.Decoder.decode_string)(sp.bytes("0x80")) == "")
    scenario.verify(
        sp.build_lambda(RLP.Decoder.decode_string)(sp.bytes("0x8454455854")) == "TEXT"
    )
    scenario.verify_equal(
        sp.build_lambda(RLP.Decoder.decode_list)(
            sp.bytes("0xcb87038d7ea4c67fff82ffff")
        ),
        sp.map({0: sp.bytes("0x87038d7ea4c67fff"), 1: sp.bytes("0x82ffff")}),
    )
