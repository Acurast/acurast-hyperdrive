import smartpy as sp

from contracts.tezos.utils.bytes import nat_of_bytes

STRING_SHORT_START = 128  # sp.bytes("0x80")
STRING_LONG_START = 184  # sp.bytes("0xb8")

LIST_SHORT_START = 192
LIST_SHORT_START_BYTES = sp.bytes("0xc0")

LIST_LONG_START = 248  # sp.bytes("0xf8")


def to_list(item):
    num_items_lambda = sp.compute(sp.build_lambda(num_items))
    item_length_lambda = sp.compute(sp.build_lambda(item_length))
    payload_offset_lambda = sp.compute(sp.build_lambda(payload_offset))
    is_list_lambda = sp.compute(sp.build_lambda(is_list))

    sp.verify(is_list_lambda(item), "Cannot convert to list a non-list RLPItem.")

    items = sp.compute(num_items_lambda(item))
    length = sp.compute(sp.len(item))
    result = sp.local("result", sp.map(tkey=sp.TNat))

    cur_pos = sp.local("cur_pos", payload_offset_lambda(item))
    with sp.for_("pos", sp.range(0, items, 1)) as pos:
        data_length = sp.compute(
            item_length_lambda(
                sp.slice(
                    item, cur_pos.value, sp.as_nat(length - cur_pos.value)
                ).open_some()
            )
        )
        result.value[pos] = sp.slice(item, cur_pos.value, data_length).open_some()
        cur_pos.value += data_length

    sp.result(result.value)


def is_list(item):
    """
    Indicates whether encoded payload is a list.
    """
    byte0 = sp.slice(item, 0, 1).open_some()
    sp.result(byte0 >= LIST_SHORT_START_BYTES)


def payload_offset(item):
    """
    Gives the number of bytes until the data
    """
    nat_of_bytes_lambda = sp.compute(sp.build_lambda(nat_of_bytes))
    byte0 = sp.compute(nat_of_bytes_lambda(sp.slice(item, 0, 1).open_some()))

    with sp.set_result_type(sp.TNat):
        with sp.if_(byte0 < STRING_SHORT_START):
            sp.result(0)
        with sp.else_():
            with sp.if_(
                (byte0 < STRING_LONG_START)
                | ((byte0 >= LIST_SHORT_START) & (byte0 < LIST_LONG_START))
            ):
                sp.result(1)
            with sp.else_():
                with sp.if_(byte0 < LIST_SHORT_START):
                    # 183 = STRING_LONG_START - 1
                    sp.result(sp.as_nat(byte0 - 183) + 1)
                with sp.else_():
                    # 247 = LIST_LONG_START - 1
                    sp.result(sp.as_nat(byte0 - 247) + 1)


def item_length(item):
    nat_of_bytes_lambda = sp.compute(sp.build_lambda(nat_of_bytes))
    byte0 = sp.compute(nat_of_bytes_lambda(sp.slice(item, 0, 1).open_some()))

    with sp.if_(byte0 < STRING_SHORT_START):
        sp.result(1)
    with sp.else_():
        with sp.if_(byte0 < STRING_LONG_START):
            sp.result(sp.as_nat((byte0 - STRING_SHORT_START) + 1))
        with sp.else_():
            with sp.if_(byte0 < LIST_SHORT_START):
                # 183 = STRING_LONG_START - 1
                bytes_length = sp.compute(sp.as_nat(byte0 - 183))
                # skip over the first byte
                _item = sp.slice(item, 1, sp.as_nat(sp.len(item) - 1)).open_some()
                # right shifting to get the length
                data_length = nat_of_bytes_lambda(
                    sp.slice(_item, 0, bytes_length).open_some()
                )
                sp.result(data_length + bytes_length + 1)
            with sp.else_():
                with sp.if_(byte0 < LIST_LONG_START):
                    sp.result(sp.as_nat((byte0 - LIST_SHORT_START) + 1))
                with sp.else_():
                    # 247 = LIST_LONG_START - 1
                    bytes_length = sp.compute(sp.as_nat(byte0 - 247))
                    # skip over the first byte
                    _item = sp.slice(item, 1, sp.as_nat(sp.len(item) - 1)).open_some()
                    # right shifting to get the length
                    data_length = nat_of_bytes_lambda(
                        sp.slice(_item, 0, bytes_length).open_some()
                    )
                    sp.result(data_length + bytes_length + 1)


def num_items(item):
    """
    Gives the number of payload items inside an encoded list.
    """
    item_length_lambda = sp.compute(sp.build_lambda(item_length))
    payload_offset_lambda = sp.compute(sp.build_lambda(payload_offset))

    count = sp.local("count", 0)
    cur_pos = sp.local("pos", payload_offset_lambda(item))
    end_pos = sp.compute(sp.len(item))
    with sp.while_(cur_pos.value < end_pos):
        cur_pos.value += item_length_lambda(
            sp.slice(
                item, cur_pos.value, sp.as_nat(end_pos - cur_pos.value)
            ).open_some()
        )  # skip over an item
        count.value += 1

    with sp.set_result_type(sp.TNat):
        sp.result(count.value)


def remove_offset(item):
    payload_offset_lambda = sp.compute(sp.build_lambda(payload_offset))

    offset = sp.compute(payload_offset_lambda(item))
    length = sp.as_nat(sp.len(item) - offset)

    with sp.set_result_type(sp.TBytes):
        sp.result(sp.slice(item, offset, length).open_some())
