import smartpy as sp

from contracts.tezos.utils.misc import generate_var

class Math:
    @staticmethod
    def pow(n, e):
        result = sp.local(generate_var("result"), 1)
        base = sp.local(generate_var("base"), n)
        exponent = sp.local(generate_var("exponent"), e)

        with sp.while_(exponent.value != 0):
            with sp.if_((exponent.value % 2) != 0):
                result.value *= base.value

            exponent.value = exponent.value >> 1  # Equivalent to exponent.value / 2
            base.value *= base.value

        return result.value
