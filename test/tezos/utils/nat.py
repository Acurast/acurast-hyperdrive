import smartpy as sp

from contracts.tezos.utils.utils import Nat


@sp.add_test(name="Util_nat")
def test():

    scenario = sp.test_scenario()

    # Test lambdas
    scenario.show(sp.build_lambda(Nat.of_bytes)(sp.bytes("0x0211")))
    scenario.verify(sp.build_lambda(Nat.of_bytes)(sp.bytes("0x0211")) == 529)
    scenario.verify(sp.build_lambda(Nat.of_bytes)(sp.bytes("0xf8")) == 248)
