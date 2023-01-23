import smartpy as sp

from contracts.tezos.libs.utils import Bytes


@sp.add_test(name="Util_bytes")
def test():

    scenario = sp.test_scenario()

    # Test lambda
    result = scenario.compute(
        sp.build_lambda(Bytes.of_nat)(
            32592575621351777380295131014550050576823494298654980010178247189670100796213387298934358015
        )
    )
    scenario.show(result)
    scenario.verify(
        result
        == sp.bytes(
            "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )
    )

    result = scenario.compute(sp.build_lambda(Bytes.of_nat)(280))
    scenario.show(result)
    scenario.verify(result == sp.bytes("0x0118"))
