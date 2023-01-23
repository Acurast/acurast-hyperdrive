import smartpy as sp

from contracts.tezos.libs.patricia_trie import split_common_prefix, chop_first_bit


@sp.add_test(name="Util_patricia_trie__split_common_prefix")
def test_split_common_prefix():

    scenario = sp.test_scenario()

    # Test lambda
    result = scenario.compute(
        sp.build_lambda(split_common_prefix)(
            (sp.record(data=15, length=4), sp.record(data=7, length=3))
        )
    )
    expected_result = sp.record(
        prefix=sp.record(data=7, length=3), suffix=sp.record(data=1, length=1)
    )

    scenario.show(result)
    scenario.verify(result == expected_result)


@sp.add_test(name="Util_patricia_trie__chop_first_bit")
def test_chop_first_bit():
    scenario = sp.test_scenario()

    label = sp.record(
        data=103467121227129887621618079513505806301059647461257568066320101310811728706554,
        length=256,
    )

    # Test lambda
    res = scenario.compute(sp.build_lambda(chop_first_bit)(label))
    scenario.verify(sp.fst(res) == 1)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 1)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 1)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 0)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 0)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 1)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 0)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 0)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 1)
    res = scenario.compute(sp.build_lambda(chop_first_bit)(sp.snd(res)))
    scenario.verify(sp.fst(res) == 1)

    scenario.show(res)
