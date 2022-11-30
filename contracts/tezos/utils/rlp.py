import smartpy as sp

from contracts.tezos.utils.bytes import Bytes
from contracts.tezos.utils.string import String
from contracts.tezos.utils.nat import Nat

STRING_SHORT_START = 128  # sp.bytes("0x80")
STRING_LONG_START = 184  # sp.bytes("0xb8")

LIST_SHORT_START = 192
LIST_SHORT_START_BYTES = sp.bytes("0xc0")

LIST_LONG_START = 248  # sp.bytes("0xf8")


class Encoder:
    @staticmethod
    def encode_length(arg):
        (length, offset) = sp.match_pair(arg)

        bytes_of_nat = sp.build_lambda(Bytes.of_nat)
        bytes_of_uint8 = sp.build_lambda(lambda x: sp.result(Bytes.of_uint8(x)))

        with sp.if_(length < 56):
            sp.result(bytes_of_uint8(offset + length))
        with sp.else_():
            with sp.if_(length < 256**8):
                encoded_length = sp.compute(bytes_of_nat(offset + length))
                sp.result(
                    bytes_of_uint8(sp.len(encoded_length) + 55 + length)
                    + encoded_length
                )
            with sp.else_():
                sp.failwith("INVALID_LENGTH")

    @staticmethod
    def encode_nat(n):
        encode = sp.build_lambda(Encoder.with_length_prefix)
        bytes_of_nat = sp.build_lambda(Bytes.of_nat)
        with sp.if_(n == 0):
            sp.result(sp.bytes("0x80"))
        with sp.else_():
            sp.result(encode(bytes_of_nat(n)))

    @staticmethod
    def encode_string(s):
        encode = sp.build_lambda(Encoder.with_length_prefix)
        bytes_of_string = sp.build_lambda(Bytes.of_string)
        with sp.if_(s == ""):
            sp.result(sp.bytes("0x80"))
        with sp.else_():
            sp.result(encode(bytes_of_string(s)))

    @staticmethod
    def with_length_prefix(b):
        encode_length = sp.build_lambda(Encoder.encode_length)
        with sp.if_(sp.len(b) == 0):
            sp.result(sp.bytes("0x80"))
        with sp.else_():
            sp.result(encode_length((sp.len(b), STRING_SHORT_START)) + b)

    @staticmethod
    def encode_list(l):
        encode_length = sp.build_lambda(Encoder.encode_length)
        with sp.if_(sp.len(l) == 0):
            sp.result(LIST_SHORT_START_BYTES)
        with sp.else_():
            l_bytes = sp.compute(sp.concat(l))
            sp.result(encode_length((sp.len(l_bytes), LIST_SHORT_START)) + l_bytes)


class Decoder:
    @staticmethod
    def is_list(item):
        """
        Indicates whether encoded payload is a list.
        """
        byte0 = sp.slice(item, 0, 1).open_some()
        sp.result(byte0 >= LIST_SHORT_START_BYTES)

    @staticmethod
    def without_length_prefix(b):
        payload_offset_lambda = sp.build_lambda(Decoder.prefix_length)

        offset = sp.compute(payload_offset_lambda(b))
        length = sp.as_nat(sp.len(b) - offset)

        sp.result(sp.slice(b, offset, length).open_some())

    @staticmethod
    def list_size(b):
        """
        Gives the number of payload items inside an encoded list.
        """
        item_length_lambda = sp.compute(sp.build_lambda(Decoder.length))
        payload_offset_lambda = sp.compute(sp.build_lambda(Decoder.prefix_length))

        count = sp.local("count", sp.nat(0))
        cur_pos = sp.local("pos", payload_offset_lambda(b))
        end_pos = sp.compute(sp.len(b))
        with sp.while_(cur_pos.value < end_pos):
            cur_pos.value += item_length_lambda(
                sp.slice(
                    b, cur_pos.value, sp.as_nat(end_pos - cur_pos.value)
                ).open_some()
            )
            # next item
            count.value += 1

        sp.result(count.value)

    @staticmethod
    def decode_list(b):
        list_size_lambda = sp.compute(sp.build_lambda(Decoder.list_size))
        item_length_lambda = sp.compute(sp.build_lambda(Decoder.length))
        payload_offset_lambda = sp.compute(sp.build_lambda(Decoder.prefix_length))
        is_list_lambda = sp.compute(sp.build_lambda(Decoder.is_list))

        sp.verify(is_list_lambda(b), "NOT_A_LIST")

        items = sp.compute(list_size_lambda(b))
        length = sp.compute(sp.len(b))
        result = sp.local("result", sp.map(tkey=sp.TNat))

        cur_pos = sp.local("cur_pos", payload_offset_lambda(b))
        with sp.for_("pos", sp.range(0, items, 1)) as pos:
            data_length = sp.compute(
                item_length_lambda(
                    sp.slice(
                        b, cur_pos.value, sp.as_nat(length - cur_pos.value)
                    ).open_some()
                )
            )
            result.value[pos] = sp.slice(b, cur_pos.value, data_length).open_some()
            cur_pos.value += data_length

        sp.result(result.value)

    @staticmethod
    def decode_nat(b):
        without_length_prefix = sp.build_lambda(Decoder.without_length_prefix)
        nat_of_bytes_lambda = sp.build_lambda(Nat.of_bytes)
        with sp.if_(b == sp.bytes("0x80")):
            sp.result(sp.nat(0))
        with sp.else_():
            sp.result(nat_of_bytes_lambda(without_length_prefix(b)))

    @staticmethod
    def decode_string(b):
        without_length_prefix = sp.build_lambda(Decoder.without_length_prefix)
        with sp.if_(b == sp.bytes("0x80")):
            sp.result("")
        with sp.else_():
            sp.result(String.of_bytes(without_length_prefix(b)))

    @staticmethod
    def length(item):
        nat_of_bytes_lambda = sp.compute(sp.build_lambda(Nat.of_bytes))
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
                        _item = sp.slice(
                            item, 1, sp.as_nat(sp.len(item) - 1)
                        ).open_some()
                        # right shifting to get the length
                        data_length = nat_of_bytes_lambda(
                            sp.slice(_item, 0, bytes_length).open_some()
                        )
                        sp.result(data_length + bytes_length + 1)

    @staticmethod
    def prefix_length(b):
        """
        Gives the number of bytes until the data
        """
        nat_of_bytes_lambda = sp.build_lambda(Nat.of_bytes)
        byte0 = sp.compute(nat_of_bytes_lambda(sp.slice(b, 0, 1).open_some()))

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


class Lambda:
    # Encoding
    encode_list = sp.build_lambda(Encoder.encode_list)
    encode_nat = sp.build_lambda(Encoder.encode_nat)
    with_length_prefix = sp.build_lambda(Encoder.with_length_prefix)
    # Decoding
    without_length_prefix = sp.build_lambda(Decoder.without_length_prefix)
    decode_nat = sp.build_lambda(Decoder.decode_nat)
    decode_list = sp.build_lambda(Decoder.decode_list)
