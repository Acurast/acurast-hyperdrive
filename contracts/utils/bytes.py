import smartpy as sp

from contracts.utils.misc import generate_var


def _hex(n: int) -> str:
    return sp.bytes("0x" + (hex(n)[2:].rjust(2, "0")))


def _bits(n: int) -> str:
    return sp.string("{0:b}".format(n).rjust(8, "0"))


bits_to_bytes = sp.map({_bits(x): _hex(x) for x in range(0, 256)})
bytes_to_bits = sp.map({_hex(x): _bits(x) for x in range(0, 256)})


def pad_start(value):
    padding = 8 - (sp.len(value) % 8)
    with sp.for_("x", sp.range(0, padding, 1)):
        value = "0" + value

    return value


def bits_of_bytes(self, b):
    bits = sp.local(generate_var("bits"), "")
    with sp.for_("x", sp.range(0, sp.len(b), 1)) as x:
        bits.value += self.data.bytes_to_bits[
            sp.slice(b, x, 1).open_some("Out of bonds")
        ]

    return bits.value


def bytes_of_bits(self, b):
    b = pad_start(b)

    _bytes = sp.local(generate_var("bytes"), sp.bytes("0x"))
    with sp.for_("x", sp.range(sp.to_int(sp.len(b)), 8, -8)) as x:
        _bytes.value = (
            self.data.bits_to_bytes[
                sp.slice(b, sp.as_nat(x - 8), 8).open_some("Out of bonds")
            ]
            + _bytes.value
        )

    return _bytes.value
