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


def split_common_prefix(arg):
    (a, b) = sp.match_pair(arg)
    sp.result(split_at(a, common_prefix(a, b)))


def split_at(bits, pos):
    """
    Splits a sequence of bits at a given position into two labels, a prefix and a suffix.

    :returns: sp.TRecord(
        prefix = Type.Label,
        suffix = Type.Label
    )
    """
    sp.verify((pos <= sp.len(bits)) & (pos <= 256), "Bad pos")

    prefix = sp.local("prefix", sp.record(length=pos, data=""))  # NULL path

    # TODO: Improve
    with sp.if_(pos != 0):
        prefix.value.data = sp.slice(bits, 0, pos).open_some("Out of bounds")

    # TODO: Improve
    suffix_length = sp.as_nat(sp.len(bits) - pos, "underflow")
    return sp.record(
        prefix=prefix.value,
        suffix=sp.record(
            length=suffix_length,
            data=sp.slice(bits, pos, suffix_length).open_some("Out of bounds"),
        ),
    )


def common_prefix(a, b):
    """
    Returns the length of the longest common prefix of the two labels.

    :returns: sp.TNat
    """
    length = sp.bind_block()
    with length:
        l_a = sp.local(generate_var("l_a"), sp.len(a)).value
        l_b = sp.local(generate_var("l_b"), sp.len(b)).value
        with sp.if_(l_a < l_b):
            sp.result(l_a)
        with sp.else_():
            sp.result(l_b)

    prefix_length = sp.local(generate_var("prefix_length"), 0)
    break_loop = sp.local(generate_var("break_loop"), False)
    with sp.while_(~break_loop.value & (prefix_length.value < length.value)):
        bit_a = sp.slice(a, prefix_length.value, 1).open_some("OUT_OF_BOUNDS")
        bit_b = sp.slice(b, prefix_length.value, 1).open_some("OUT_OF_BOUNDS")

        with sp.if_(bit_a == bit_b):
            prefix_length.value += 1
        with sp.else_():
            break_loop.value = True

    return prefix_length.value


def chop_first_bit(label):
    """
    Builds a pair that has as first element the first bit of a label and
    as second element a new label without that first bit.

    :returns: sp.TPair(sp.TNat, Type.Label)
    """
    sp.verify(label.length > 0, "EMPTY_LABEL")

    first_bit = sp.bind_block()
    with first_bit:
        bit = sp.slice(label.data, 0, 1).open_some(
            0
        )  # Cannot fail, already validated above
        with sp.if_(bit == "0"):
            sp.result(sp.int(0))
        with sp.else_():
            sp.result(sp.int(1))

    tail_length = sp.as_nat(label.length - 1, 0)  # Cannot fail, already validated above
    tail = sp.slice(label.data, 1, tail_length).open_some("OUT_OF_BOUNDS")

    sp.result((first_bit.value, sp.record(length=tail_length, data=tail)))


def remove_prefix(arg):
    """
    Builds a new label after removing a given `prefix_length`.

    :returns: Type.Label
    """
    (label, prefix_length) = sp.match_pair(arg)

    length = sp.compute(sp.as_nat(label.length - prefix_length, "PREFIX_TOO_LONG"))

    new_label = sp.bind_block()
    with new_label:
        with sp.if_(length == 0):
            sp.result(sp.record(length=0, data=""))
        with sp.else_():
            sp.result(
                sp.record(
                    length=length,
                    data=sp.slice(label.data, prefix_length, length).open_some(
                        "PREFIX_LONGER_THAN_DATA"
                    ),
                )
            )

    sp.result(new_label.value)
