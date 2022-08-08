import smartpy as sp

import contracts.tezos.utils.bytes as Bytes


@sp.add_test(name="Util_bytes")
def test():

    scenario = sp.test_scenario()

    # Test lambdas
    scenario.show(sp.build_lambda(Bytes.nat_of_bytes)(sp.bytes("0x0211")))
    scenario.verify(sp.build_lambda(Bytes.nat_of_bytes)(sp.bytes("0x0211")) == 529)
    scenario.verify(sp.build_lambda(Bytes.nat_of_bytes)(sp.bytes("0xf8")) == 248)
