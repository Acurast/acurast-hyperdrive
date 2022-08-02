import smartpy as sp

latest_var_id = 0


def generate_var(postfix=None):
    """
    Generate a unique variable name

    Necessary because of smartpy code inlining
    """
    global latest_var_id

    id = "utils_%s%s" % (latest_var_id, ("_" + postfix if postfix is not None else ""))
    latest_var_id += 1

    return id


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


def int_of_bits(bstring):
    n = sp.local("n", 0)
    length = sp.compute(sp.len(bstring) - 1)
    with sp.for_("p", sp.range(0, length + 1, 1)) as p:
        with sp.if_(sp.slice(bstring, abs(p), 1) == sp.some("1")):
            n.value += pow(2, abs(length - p))

    sp.result(n.value)


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


def get_suffix(b, length):
    return b & sp.as_nat((1 << length) - 1)


def get_prefix(b, full_length, prefix_length):
    return b >> sp.as_nat(full_length - prefix_length)


def is_bit_set(i, n):
    return (i >> n) & 1


def int_of_bytes(b):
    _bytes = sp.local("bytes", sp.bytes("0x"))
    # Reverse bytes for (little-endian)
    size = sp.compute(sp.len(b))
    with sp.for_("pos", sp.range(0, size)) as pos:
        byte0 = sp.slice(b, pos, 1).open_some()
        _bytes.value = byte0 + _bytes.value
    # Pad 0x to the right until bytes length is 32
    with sp.while_(sp.len(_bytes.value) < 32):
        _bytes.value = _bytes.value + sp.bytes("0x00")
    # Append (packed prefix) + (Data identifier) + (Length) + (Data)
    # - Packed prefix: 0x05 (1 byte)
    # - Data identifier: (bls12_381_fr = 0x0a) (1 byte)
    # - Length ("0x00000020" = 32) (4 bytes)
    # - Data
    packedBytes = sp.bytes("0x050a00000020") + _bytes.value
    sp.result(
        sp.as_nat(sp.to_int(sp.unpack(packedBytes, sp.TBls12_381_fr).open_some()))
    )
