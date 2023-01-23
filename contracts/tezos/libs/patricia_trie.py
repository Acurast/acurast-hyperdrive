import smartpy as sp

from contracts.tezos.libs.misc import generate_var

HASH_FUNCTION = sp.keccak
HASH_LENGTH = 256
NULL_HASH = sp.bytes("0x")

EMPTY_TREE = sp.record(
    root=NULL_HASH,
    root_edge=sp.record(
        node=NULL_HASH,
        label=sp.record(data=0, length=0),
    ),
    nodes=sp.map(),
    states=sp.map(),
)


def get_suffix(b, length):
    return b & sp.as_nat((1 << length) - 1)


def get_prefix(b, full_length, prefix_length):
    return b >> sp.as_nat(full_length - prefix_length)


def split_common_prefix(arg):
    (a, b) = sp.match_pair(arg)
    sp.result(split_at((a, common_prefix(a, b))))


def split_at(arg):
    """
    Splits a sequence of bits at a given position into two keys, a prefix and a suffix.

    :returns: sp.TRecord(
        prefix = Type.KeyMeta,
        suffix = Type.KeyMeta
    )
    """
    (l, pos) = sp.match_pair(arg)
    sp.verify((pos <= l.length) & (pos <= 256), "BAD_POS")

    prefix = sp.local("prefix", sp.record(length=pos, data=0))  # NULL path

    with sp.if_(pos != 0):
        prefix.value.data = get_prefix(l.data, l.length, pos)

    suffix_length = sp.as_nat(l.length - pos, 0)  # Cannot fail, checked above
    return sp.record(
        prefix=prefix.value,
        suffix=sp.record(
            length=suffix_length,
            data=get_suffix(l.data, suffix_length),
        ),
    )


def common_prefix(a, b):
    """
    Returns the length of the longest common prefix of the two keys.

    :returns: sp.TNat
    """
    length = sp.bind_block()
    with length:
        with sp.if_(a.length < b.length):
            sp.result(a.length)
        with sp.else_():
            sp.result(b.length)

    prefix_length = sp.local(generate_var("prefix_length"), 0)
    break_loop = sp.local(generate_var("break_loop"), False)
    with sp.while_(~break_loop.value & (prefix_length.value < length.value)):
        bit_a = get_prefix(a.data, a.length, prefix_length.value + 1)
        bit_b = get_prefix(b.data, b.length, prefix_length.value + 1)

        with sp.if_(bit_a == bit_b):
            prefix_length.value += 1
        with sp.else_():
            break_loop.value = True

    return prefix_length.value


def chop_first_bit(key):
    """
    Builds a pair that has as first element the first bit of a key and
    as second element a new key without that first bit.

    :returns: sp.TPair(sp.TNat, Type.KeyMeta)
    """
    sp.verify(key.length > 0, "EMPTY_KEY")

    tail_length = sp.as_nat(key.length - 1, 0)  # Cannot fail, already validated above
    tail = get_suffix(key.data, tail_length)
    first_bit = sp.to_int(key.data >> tail_length)

    sp.result((first_bit, sp.record(length=tail_length, data=tail)))


def remove_prefix(arg):
    """
    Builds a new key after removing a given `prefix_length`.

    :returns: Type.KeyMeta
    """
    (key, prefix_length) = sp.match_pair(arg)

    length = sp.compute(sp.as_nat(key.length - prefix_length, "PREFIX_TOO_LONG"))

    new_key = sp.bind_block()
    with new_key:
        with sp.if_(length == 0):
            sp.result(sp.record(length=0, data=0))
        with sp.else_():
            sp.result(
                sp.record(
                    length=length,
                    data=get_suffix(key.data, length),
                )
            )

    sp.result(new_key.value)
