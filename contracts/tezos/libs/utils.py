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


class String:
    @staticmethod
    def of_bytes(b):
        bytes_of_nat = sp.build_lambda(Bytes.of_nat)
        # Encode the string length
        # Each utf-8 char is represented by 2 nibble (1 byte)
        lengthBytes = sp.local("lengthBytes", bytes_of_nat(sp.len(b)))
        with sp.while_(sp.len(lengthBytes.value) < 4):
            lengthBytes.value = sp.bytes("0x00") + lengthBytes.value
        # Append (packed prefix) + (Data identifier) + (string length) + (string bytes)
        # - Packed prefix: 0x05 (1 byte)
        # - Data identifier: (string = 0x01) (1 byte)
        # - String length (4 bytes)
        # - String bytes
        packedBytes = sp.concat(
            [sp.bytes("0x05"), sp.bytes("0x01"), lengthBytes.value, b]
        )
        return sp.unpack(packedBytes, sp.TString).open_some(
            "Could not decode bytes to string"
        )


class Nat:
    @staticmethod
    def of_bytes(b):
        length = sp.compute(sp.len(b))
        decimal = sp.local("decimal", sp.nat(0))
        with sp.for_("_pos", sp.range(0, length)) as pos:
            byte = sp.compute(sp.slice(b, pos, 1).open_some())
            base = sp.compute(sp.as_nat(length - (pos + 1)) * 2)
            # - Packed prefix: 0x05 (1 byte)
            # - Data identifier: (bytes = 0x0a) (1 byte)
            # - Length ("0x00000020" = 32) (4 bytes)
            # - Data (32 bytes)
            packedBytes = sp.bytes("0x050a00000020") + byte + sp.bytes("0x" + "00" * 31)
            decimal.value += sp.as_nat(
                sp.to_int(sp.unpack(packedBytes, sp.TBls12_381_fr).open_some())
            ) * Math.pow(16, base)

        sp.result(decimal.value)


class RLP:
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
            bytes_of_nat8 = sp.build_lambda(lambda x: sp.result(Bytes.of_nat8(x)))

            with sp.if_(length < 56):
                sp.result(bytes_of_nat8(offset + length))
            with sp.else_():
                with sp.if_(length < 256**8):
                    encoded_length = sp.compute(bytes_of_nat(offset + length))
                    sp.result(
                        bytes_of_nat8(sp.len(encoded_length) + 55 + length)
                        + encoded_length
                    )
                with sp.else_():
                    sp.failwith("INVALID_LENGTH")

        @staticmethod
        def encode_nat(n):
            b = sp.compute(sp.build_lambda(Bytes.of_nat)(n))
            with sp.if_(n < RLP.STRING_SHORT_START):
                sp.result(b)
            with sp.else_():
                encode = sp.build_lambda(RLP.Encoder.with_length_prefix)
                sp.result(encode(b))

        @staticmethod
        def encode_string(s):
            encode = sp.build_lambda(RLP.Encoder.with_length_prefix)
            bytes_of_string = sp.build_lambda(Bytes.of_string)
            with sp.if_(s == ""):
                sp.result(sp.bytes("0x80"))
            with sp.else_():
                sp.result(encode(bytes_of_string(s)))

        @staticmethod
        def with_length_prefix(b):
            encode_length = sp.build_lambda(RLP.Encoder.encode_length)
            with sp.if_(sp.len(b) == 0):
                sp.result(sp.bytes("0x80"))
            with sp.else_():
                sp.result(encode_length((sp.len(b), RLP.STRING_SHORT_START)) + b)

        @staticmethod
        def encode_list(l):
            encode_length = sp.build_lambda(RLP.Encoder.encode_length)
            with sp.if_(sp.len(l) == 0):
                sp.result(RLP.LIST_SHORT_START_BYTES)
            with sp.else_():
                l_bytes = sp.compute(sp.concat(l))
                sp.result(
                    encode_length((sp.len(l_bytes), RLP.LIST_SHORT_START)) + l_bytes
                )

    class Decoder:
        @staticmethod
        def is_list(item):
            """
            Indicates whether encoded payload is a list.
            """
            byte0 = sp.slice(item, 0, 1).open_some()
            sp.result(byte0 >= RLP.LIST_SHORT_START_BYTES)

        @staticmethod
        def without_length_prefix(b):
            payload_offset_lambda = sp.build_lambda(RLP.Decoder.prefix_length)

            offset = sp.compute(payload_offset_lambda(b))
            length = sp.as_nat(sp.len(b) - offset)

            sp.result(sp.slice(b, offset, length).open_some())

        @staticmethod
        def list_size(b):
            """
            Gives the number of payload items inside an encoded list.
            """
            item_length_lambda = sp.compute(sp.build_lambda(RLP.Decoder.length))
            payload_offset_lambda = sp.compute(
                sp.build_lambda(RLP.Decoder.prefix_length)
            )

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
            list_size_lambda = sp.compute(sp.build_lambda(RLP.Decoder.list_size))
            item_length_lambda = sp.compute(sp.build_lambda(RLP.Decoder.length))
            payload_offset_lambda = sp.compute(
                sp.build_lambda(RLP.Decoder.prefix_length)
            )
            is_list_lambda = sp.compute(sp.build_lambda(RLP.Decoder.is_list))

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
            without_length_prefix = sp.build_lambda(RLP.Decoder.without_length_prefix)
            nat_of_bytes_lambda = sp.build_lambda(Nat.of_bytes)
            with sp.if_(b == sp.bytes("0x80")):
                sp.result(sp.nat(0))
            with sp.else_():
                sp.result(nat_of_bytes_lambda(without_length_prefix(b)))

        @staticmethod
        def decode_string(b):
            without_length_prefix = sp.build_lambda(RLP.Decoder.without_length_prefix)
            with sp.if_(b == sp.bytes("0x80")):
                sp.result("")
            with sp.else_():
                sp.result(String.of_bytes(without_length_prefix(b)))

        @staticmethod
        def length(item):
            nat_of_bytes_lambda = sp.compute(sp.build_lambda(Nat.of_bytes))
            byte0 = sp.compute(nat_of_bytes_lambda(sp.slice(item, 0, 1).open_some()))

            with sp.if_(byte0 < RLP.STRING_SHORT_START):
                sp.result(1)
            with sp.else_():
                with sp.if_(byte0 < RLP.STRING_LONG_START):
                    sp.result(sp.as_nat((byte0 - RLP.STRING_SHORT_START) + 1))
                with sp.else_():
                    with sp.if_(byte0 < RLP.LIST_SHORT_START):
                        # 183 = STRING_LONG_START - 1
                        bytes_length = sp.compute(sp.as_nat(byte0 - 183))
                        # skip over the first byte
                        _item = sp.slice(
                            item, 1, sp.as_nat(sp.len(item) - 1)
                        ).open_some()
                        # right shifting to get the length
                        data_length = nat_of_bytes_lambda(
                            sp.slice(_item, 0, bytes_length).open_some()
                        )
                        sp.result(data_length + bytes_length + 1)
                    with sp.else_():
                        with sp.if_(byte0 < RLP.LIST_LONG_START):
                            sp.result(sp.as_nat((byte0 - RLP.LIST_SHORT_START) + 1))
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
                with sp.if_(byte0 < RLP.STRING_SHORT_START):
                    sp.result(0)
                with sp.else_():
                    with sp.if_(
                        (byte0 < RLP.STRING_LONG_START)
                        | (
                            (byte0 >= RLP.LIST_SHORT_START)
                            & (byte0 < RLP.LIST_LONG_START)
                        )
                    ):
                        sp.result(1)
                    with sp.else_():
                        with sp.if_(byte0 < RLP.LIST_SHORT_START):
                            # 183 = STRING_LONG_START - 1
                            sp.result(sp.as_nat(byte0 - 183) + 1)
                        with sp.else_():
                            # 247 = LIST_LONG_START - 1
                            sp.result(sp.as_nat(byte0 - 247) + 1)

    class Lambda:
        # Encoding
        @staticmethod
        def encode_list():
            return sp.build_lambda(RLP.Encoder.encode_list)

        @staticmethod
        def encode_nat():
            return sp.build_lambda(RLP.Encoder.encode_nat)

        @staticmethod
        def with_length_prefix():
            return sp.build_lambda(RLP.Encoder.with_length_prefix)

        # Decoding
        @staticmethod
        def without_length_prefix():
            return sp.build_lambda(RLP.Decoder.without_length_prefix)

        @staticmethod
        def decode_nat():
            return sp.build_lambda(RLP.Decoder.decode_nat)

        @staticmethod
        def decode_list():
            return sp.build_lambda(RLP.Decoder.decode_list)

        @staticmethod
        def decode_string():
            return sp.build_lambda(RLP.Decoder.decode_string)


class EvmStorage:
    @staticmethod
    def read_string_slot(b):
        """
        Read string from EVM storage slot

        Details: https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html#bytes-and-string
        """
        lowest_byte = sp.slice(b, abs(sp.len(b) - 1), 1).open_some()
        # If lowest byte is set, it means the string is stored in the slot and the lowest byte is the length
        sp.verify(lowest_byte != sp.bytes("0x00"), "MULTIPLE_SLOT_READ_NOT_SUPPORTED")

        string_length = RLP.Lambda.decode_nat()(lowest_byte) / 2
        string_bytes = sp.slice(b, 0, string_length + 1).open_some()

        sp.result(RLP.Lambda.decode_string()(string_bytes))

    @staticmethod
    def write_uint_slot(n):
        """
        Write nat as an EVM storage slot

        Details: https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html
        """
        pad_start_lambda = sp.build_lambda(Bytes.pad_start)
        sp.result(pad_start_lambda((RLP.Lambda.encode_nat()(n), sp.bytes("0x00"), 32)))
