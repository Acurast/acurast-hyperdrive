import smartpy as sp

from contracts.tezos.utils.misc import generate_var


class Bytes:
    @staticmethod
    def pad_start(arg):
        (b, fill, length) = sp.match_tuple(arg, "el1", "el2", "el3")
        diff = sp.compute(sp.as_nat(length - sp.len(b)))
        prefix = sp.local(generate_var("bytes"), sp.bytes("0x"))

        with sp.while_(sp.len(prefix.value) < diff):
            prefix.value = fill + prefix.value

        sp.result(prefix.value + b)

    @staticmethod
    def of_string(text):
        b = sp.pack(text)
        # Remove (packed prefix), (Data identifier) and (string length)
        # - Packed prefix: 0x05 (1 byte)
        # - Data identifier: (string = 0x01) (1 byte)
        # - String length (4 bytes)
        sp.result(
            sp.slice(b, 6, sp.as_nat(sp.len(b) - 6)).open_some(
                "Could not encode string to bytes."
            )
        )

    @staticmethod
    def of_nat8(n):
        """Convert 8-bit nat into bytes"""
        sp.verify(n < 256, "NUMBER_TOO_BIG")
        return sp.slice(
            sp.pack(sp.mul(sp.to_int(n), sp.bls12_381_fr("0x01"))), 6, 1
        ).open_some()

    @staticmethod
    def of_nat(n):
        with sp.if_(n == 0):
            sp.result(sp.bytes("0x00"))
        with sp.else_():
            value = sp.local(generate_var("value"), sp.set_type_expr(n, sp.TNat))
            left_nibble = sp.local(generate_var("left_nibble"), sp.none)
            bytes = sp.local(generate_var("bytes"), [])
            with sp.while_(value.value != 0):
                (quotient, remainder) = sp.match_pair(
                    sp.ediv(value.value, 16).open_some()
                )
                value.value = quotient
                with left_nibble.value.match_cases() as arg:
                    with arg.match("Some") as v:
                        left_nibble.value = sp.none
                        bytes.value.push(Bytes.of_nat8((remainder << 4) | v))
                    with arg.match("None"):
                        left_nibble.value = sp.some(remainder)

            with left_nibble.value.match_cases() as arg:
                with arg.match("Some") as v:
                    left_nibble.value = sp.none
                    bytes.value.push(Bytes.of_nat8((0 << 4) | v))

            sp.result(sp.concat(bytes.value))


"""
########################################################################
Legacy code (Not being used currently, but may be useful in the future)
########################################################################
"""


def is_bit_set(i, n):
    return (i >> n) & 1


def int_of_bits(bstring):
    n = sp.local("n", 0)
    length = sp.compute(sp.len(bstring) - 1)
    with sp.for_("p", sp.range(0, length + 1, 1)) as p:
        with sp.if_(sp.slice(bstring, abs(p), 1) == sp.some("1")):
            n.value += pow(2, abs(length - p))

    sp.result(n.value)


def int_of_bytes(b):
    size = sp.compute(sp.len(b))
    sp.verify(size < 32, "EXPECTED_LESS_THAN_32_BYTES")
    _bytes = sp.local("bytes", sp.bytes("0x"))
    # Reverse bytes for (little-endian)
    with sp.for_("pos", sp.range(0, size)) as pos:
        byte0 = sp.slice(b, pos, 1).open_some(sp.unit)
        _bytes.value = byte0 + _bytes.value
    # Pad 0x to the right until bytes length is 32
    with sp.while_(sp.len(_bytes.value) < 32):
        _bytes.value = _bytes.value + sp.bytes("0x00")
    # Append (packed prefix) + (Data identifier) + (Length) + (Data)
    # - Packed prefix: 0x05 (1 byte)
    # - Data identifier: (bytes = 0x0a) (1 byte)
    # - Length ("0x00000020" = 32) (4 bytes)
    # - Data
    packedBytes = sp.bytes("0x050a00000020") + _bytes.value
    sp.result(
        sp.as_nat(
            sp.to_int(sp.unpack(packedBytes, sp.TBls12_381_fr).open_some(sp.unit))
        )
    )


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


def bits_of_bytes(bytes_to_bits, b):
    bits = sp.local(generate_var("bits"), "")
    with sp.for_("x", sp.range(0, sp.len(b), 1)) as x:
        bits.value += bytes_to_bits[sp.slice(b, x, 1).open_some("Out of bonds")]

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
