# --------------------------------------------------------------------------
# This contract validates proofs generated from `eth_getProof` ethereum RPC.
#
# More info: https://eips.ethereum.org/EIPS/eip-1186
# ---------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type
import contracts.tezos.utils.rlp as RLP
import contracts.tezos.utils.bytes as Bytes

HASH_FUNCTION = sp.keccak
EMPTY_TRIE_ROOT_HASH = sp.bytes(
    "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"
)
BLOCK_HEADER_STATE_ROOT_INDEX = 3
BLOCK_HEADER_LEVEL_INDEX = 8
ACCOUNT_STORAGE_ROOT_INDEX = 2


class Error:
    INVALID_BLOCK_HEADER = "INVALID_BLOCK_HEADER"
    NOT_REGISTERED_ACCOUNT = "NOT_REGISTERED_ACCOUNT"
    NOT_VALIDATOR = "NOT_VALIDATOR"
    UNPROCESSED_STORAGE_ROOT = "UNPROCESSED_STORAGE_ROOT"


class Type:
    # Views
    VerifyArgument = sp.TRecord(
        rlp=sp.TRecord(
            to_list=sp.TLambda(sp.TBytes, sp.TMap(sp.TNat, sp.TBytes)),
            is_list=sp.TLambda(sp.TBytes, sp.TBool),
            remove_offset=sp.TLambda(sp.TBytes, sp.TBytes),
        ).right_comb(),
        proof_rlp=sp.TBytes,
        state_root=sp.TBytes,
        path=sp.TBytes,
    ).right_comb()


def get_info_from_block_header(rlp, block_header, block_hash):
    """
    Extract state root from block header, verifying block hash
    """
    sp.verify(HASH_FUNCTION(block_header) == block_hash, Error.INVALID_BLOCK_HEADER)

    int_of_bytes = sp.compute(sp.build_lambda(Bytes.int_of_bytes))

    header_fields = sp.compute(rlp.to_list(block_header))

    # Get state root hash
    state_root = rlp.remove_offset(header_fields[BLOCK_HEADER_STATE_ROOT_INDEX])
    # Get block level
    block_number = int_of_bytes(
        rlp.remove_offset(header_fields[BLOCK_HEADER_LEVEL_INDEX])
    )

    return sp.record(
        state_root=state_root,
        block_number=block_number,
    )


class IBCF_Eth_Validator(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                config=sp.TRecord(
                    # Multi-sig address allowed to manage the contract
                    administrator=sp.TAddress,
                    # Validators
                    validators=sp.TSet(sp.TAddress),
                    # Ethereum addresses being monitored
                    eth_accounts=sp.TSet(sp.TBytes),
                ),
                storage_root=sp.TBigMap(
                    sp.TPair(sp.TBytes, sp.TNat),
                    sp.TMap(sp.TAddress, sp.TBytes),
                ),
            )
        )

    @sp.onchain_view()
    def verify(self, arg):
        (rlp, proof_rlp, state_root, path32) = sp.match_record(
            sp.set_type_expr(
                arg,
                Type.VerifyArgument,
            ),
            "rlp",
            "proof_rlp",
            "state_root",
            "path",
        )

        proof_nodes = sp.compute(rlp.to_list(proof_rlp))

        proof_nodes_length = sp.compute(sp.len(proof_nodes))
        path = sp.compute(
            sp.view(
                "nibbles_of_bytes",
                sp.self_address,
                sp.record(bytes=path32, skip=sp.nat(0)),
                t=sp.TBytes,
            ).open_some("Invalid view")
        )
        full_path_length = sp.compute(sp.len(path))
        path_offset = sp.local("path_offset", 0)

        with sp.if_(proof_nodes_length == 0):
            # Root hash of empty tx trie
            sp.verify(state_root == EMPTY_TRIE_ROOT_HASH, "Bad empty proof")
            sp.result(sp.bytes("0x"))
        with sp.else_():
            next_hash = sp.local("next_hash", sp.bytes("0x"))

            continue_loop = sp.local("continue_loop", True)
            result = sp.local("result0", sp.bytes("0x"))
            with sp.for_(
                "proof_node_idx", sp.range(0, proof_nodes_length)
            ) as proof_node_idx:
                proof_node = sp.compute(proof_nodes[proof_node_idx])
                with sp.if_(continue_loop.value):

                    with sp.if_(next_hash.value == sp.bytes("0x")):
                        sp.verify(
                            state_root == HASH_FUNCTION(proof_node),
                            "Bad first proof part",
                        )
                    with sp.else_():
                        sp.verify(
                            next_hash.value == HASH_FUNCTION(proof_node), "Bad hash"
                        )

                    nodes = sp.compute(rlp.to_list(proof_node))
                    nodes_length = sp.compute(sp.len(nodes))
                    # Extension or Leaf node
                    with sp.if_(nodes_length == 2):
                        node_path = sp.compute(
                            sp.view(
                                "merkle_patricia_compact_decode",
                                sp.self_address,
                                rlp.remove_offset(nodes[0]),
                                t=sp.TBytes,
                            ).open_some("Invalid view")
                        )
                        path_offset.value += sp.compute(
                            sp.view(
                                "shared_prefix_length",
                                sp.self_address,
                                sp.record(
                                    path_offset=path_offset.value,
                                    full_path=path,
                                    path=node_path,
                                ),
                                t=sp.TNat,
                            ).open_some("Invalid view")
                        )
                        # last proof item
                        with sp.if_(proof_node_idx + 1 == proof_nodes_length):
                            sp.verify(
                                path_offset.value == full_path_length,
                                "Unexpected end of proof (leaf)",
                            )
                            result.value = rlp.remove_offset(
                                nodes[1]
                            )  # Data is the second item in a leaf node
                            continue_loop.value = False
                        with sp.else_():
                            # not last proof item
                            children = sp.compute(nodes[1])
                            with sp.if_(rlp.is_list(children)):
                                next_hash.value = HASH_FUNCTION(children)
                            with sp.else_():
                                next_hash.value = sp.compute(get_next_hash(children))

                    with sp.else_():
                        # Must be a branch node at this point
                        sp.verify(nodes_length == 17, "Invalid node length")

                        with sp.if_(proof_node_idx + 1 == proof_nodes_length):
                            # Proof ends in a branch node, exclusion proof in most cases
                            with sp.if_(path_offset.value + 1 == full_path_length):
                                result.value = rlp.remove_offset(nodes[16])
                                continue_loop.value = False
                            with sp.else_():
                                node_index = sp.compute(
                                    sp.view(
                                        "extract_nibble",
                                        sp.self_address,
                                        sp.record(
                                            position=path_offset.value, path=path32
                                        ),
                                        t=sp.TNat,
                                    ).open_some("Invalid view")
                                )

                                children = nodes[node_index]

                                # Ensure that the next path item is empty, end of exclusion proof
                                sp.verify(
                                    sp.len(nodes[node_index]) == 0,
                                    "Invalid exclusion proof",
                                )
                                result.value = sp.bytes("0x")
                                continue_loop.value = False

                        with sp.else_():
                            sp.verify(
                                path_offset.value < sp.len(path),
                                "Continuing branch has depleted path",
                            )

                            node_index = sp.compute(
                                sp.view(
                                    "extract_nibble",
                                    sp.self_address,
                                    sp.record(position=path_offset.value, path=path32),
                                    t=sp.TNat,
                                ).open_some("Invalid view")
                            )

                            children = sp.compute(nodes[node_index])

                            # advance by one
                            path_offset.value += 1

                            # not last level
                            with sp.if_(rlp.is_list(children)):
                                next_hash.value = HASH_FUNCTION(children)
                            with sp.else_():
                                next_hash.value = sp.compute(get_next_hash(children))

            sp.result(result.value)

    @sp.entry_point()
    def submit_account_proof(self, arg):
        (account, block_hash, block_header, account_state_proof) = sp.match_record(
            sp.set_type_expr(
                arg,
                sp.TRecord(
                    account=sp.TBytes,
                    block_hash=sp.TBytes,
                    block_header=sp.TBytes,
                    account_state_proof=sp.TBytes,
                ).right_comb(),
            ),
            "account",
            "block_hash",
            "block_header",
            "account_state_proof",
        )
        rlp = sp.record(
            to_list=sp.compute(sp.build_lambda(RLP.to_list)),
            is_list=sp.compute(sp.build_lambda(RLP.is_list)),
            remove_offset=sp.compute(sp.build_lambda(RLP.remove_offset)),
        )

        # Check if address is allowed
        sp.verify(
            self.data.config.eth_accounts.contains(account),
            Error.NOT_REGISTERED_ACCOUNT,
        )
        # Check if sender is validator
        sp.verify(self.data.config.validators.contains(sp.sender), Error.NOT_VALIDATOR)

        # Decode block header and extract the state_root and block_number
        block_header = sp.compute(
            get_info_from_block_header(rlp, block_header, block_hash)
        )

        # The path to the contract state is the hash of the contract address
        account_state_path = HASH_FUNCTION(account)

        # Validate proof and extract the account state
        account_state_rlp_encoded = sp.compute(
            sp.view(
                "verify",
                sp.self_address,
                sp.set_type_expr(
                    sp.record(
                        path=account_state_path,
                        proof_rlp=account_state_proof,
                        rlp=rlp,
                        state_root=block_header.state_root,
                    ),
                    Type.VerifyArgument,
                ),
                t=sp.TBytes,
            ).open_some("Invalid view")
        )
        # Get account storage root hash and store it
        account_storage_root = rlp.remove_offset(
            rlp.to_list(account_state_rlp_encoded)[ACCOUNT_STORAGE_ROOT_INDEX]
        )
        with sp.if_(
            self.data.storage_root.contains(sp.pair(account, block_header.block_number))
        ):
            self.data.storage_root[sp.pair(account, block_header.block_number)][
                sp.sender
            ] = account_storage_root
        with sp.else_():
            self.data.storage_root[(account, block_header.block_number)] = sp.map(
                {sp.sender: account_storage_root}
            )

    @sp.onchain_view()
    def get_storage(self, arg):
        (account, block_number, storage_slot, storage_proof) = sp.match_record(
            sp.set_type_expr(
                arg,
                sp.TRecord(
                    account=sp.TBytes,
                    block_number=sp.TNat,
                    storage_slot=sp.TBytes,
                    storage_proof=sp.TBytes,
                ),
            ),
            "account",
            "block_number",
            "storage_slot",
            "storage_proof",
        )

        key = sp.pair(account, block_number)
        contract_root_state = sp.compute(
            self.data.storage_root.get(key, message=Error.UNPROCESSED_STORAGE_ROOT)
        )
        root_hash = sp.local("root_hash", sp.bytes("0x"))
        most_validated_count = sp.local("submission_count", 0)
        with sp.for_("entry", contract_root_state.items()) as entry:
            length = sp.compute(sp.len(entry.value))
            with sp.if_(length > most_validated_count.value):
                root_hash.value = entry.key
                most_validated_count.value = length

        rlp = sp.record(
            to_list=sp.compute(sp.build_lambda(RLP.to_list)),
            is_list=sp.compute(sp.build_lambda(RLP.is_list)),
            remove_offset=sp.compute(sp.build_lambda(RLP.remove_offset)),
        )

        sp.result(
            sp.view(
                "verify",
                sp.self_address,
                sp.set_type_expr(
                    sp.record(
                        rlp=rlp,
                        proof_rlp=storage_proof,
                        state_root=root_hash.value,
                        path=HASH_FUNCTION(storage_slot),
                    ),
                    Type.VerifyArgument,
                ),
                t=sp.TBytes,
            ).open_some("Invalid view")
        )

    @sp.onchain_view()
    def merkle_patricia_compact_decode(self, _bytes):
        sp.verify(sp.len(_bytes) > 0, "Empty bytes array")

        nat_of_bytes_lambda = sp.compute(sp.build_lambda(RLP.int_of_bytes))

        byte0 = sp.compute(nat_of_bytes_lambda(sp.slice(_bytes, 0, 1).open_some()))
        first_nibble = sp.compute(byte0 >> 4)
        nibbles_to_skip = sp.local("nibbles_to_skip", sp.nat(0))

        with sp.if_(first_nibble == 0):
            nibbles_to_skip.value = 2
        with sp.else_():
            with sp.if_(first_nibble == 1):
                nibbles_to_skip.value = 1
            with sp.else_():
                with sp.if_(first_nibble == 2):
                    nibbles_to_skip.value = 2
                with sp.else_():
                    with sp.if_(first_nibble == 3):
                        nibbles_to_skip.value = 1
                    with sp.else_():
                        # Not supposed to happen!
                        sp.failwith(("UNEXPECTED", first_nibble, _bytes))

        sp.result(
            sp.view(
                "nibbles_of_bytes",
                sp.self_address,
                sp.record(bytes=_bytes, skip=nibbles_to_skip.value),
                t=sp.TBytes,
            ).open_some("Invalid view")
        )

    @sp.onchain_view()
    def nibbles_of_bytes(self, arg):
        """
        Convert bytes to nibbels (e.g. 0xff => 0x0f0f)
        """
        (_bytes, skip_nibbles) = sp.match_record(
            sp.set_type_expr(arg, sp.TRecord(bytes=sp.TBytes, skip=sp.TNat)),
            "bytes",
            "skip",
        )

        nat_of_bytes_lambda = sp.compute(sp.build_lambda(RLP.int_of_bytes))

        bytes_length = sp.compute(sp.len(_bytes))
        sp.verify(bytes_length > 0, "Empty bytes array")

        nibbles_length = sp.compute(bytes_length * 2)
        sp.verify(nibbles_length >= skip_nibbles, "Skip nibbles amount too large")

        nibbles = sp.local("nibbles", sp.bytes("0x"))

        with sp.for_("i", sp.range(skip_nibbles, nibbles_length, 1)) as i:
            byte = sp.compute(
                nat_of_bytes_lambda(sp.slice(_bytes, i // 2, 1).open_some())
            )
            bit_pos = sp.compute(sp.map({0: 4, 1: 0}))
            nibbles.value += sp.slice(
                sp.pack((byte >> bit_pos[i % 2]) & 15), 2, 1
            ).open_some()

        sp.result(nibbles.value)

    @sp.onchain_view()
    def shared_prefix_length(self, arg):
        (path_offset, full_path, path) = sp.match_record(
            sp.set_type_expr(
                arg,
                sp.TRecord(path_offset=sp.TNat, full_path=sp.TBytes, path=sp.TBytes),
            ),
            "path_offset",
            "full_path",
            "path",
        )
        i = sp.local("i", 0)
        continue_loop = sp.local("continue", True)
        xs_length = sp.compute(sp.len(full_path))
        ys_length = sp.compute(sp.len(path))
        with sp.while_(
            continue_loop.value
            & (i.value + path_offset < xs_length)
            & (i.value < ys_length)
        ):
            p1 = sp.slice(full_path, i.value + path_offset, 1).open_some()
            p2 = sp.slice(path, i.value, 1).open_some()
            with sp.if_(p1 != p2):
                continue_loop.value = False
            with sp.else_():
                i.value += 1

        sp.result(i.value)

    @sp.onchain_view()
    def extract_nibble(self, arg):
        """
        Nibble is extracted as the least significant nibble in the returned byte
        """
        (path, position) = sp.match_record(
            sp.set_type_expr(arg, sp.TRecord(path=sp.TBytes, position=sp.TNat)),
            "path",
            "position",
        )

        nat_of_bytes_lambda = sp.compute(sp.build_lambda(RLP.int_of_bytes))

        sp.verify(position < 64, "Invalid nibble position")

        byte = sp.local(
            "byte",
            nat_of_bytes_lambda(
                sp.compute(sp.slice(path, position / 2, 1).open_some())
            ),
        )
        with sp.if_(position % 2 == 0):
            sp.result(byte.value >> 4)
        with sp.else_():
            sp.result(byte.value & 0xF)


def get_next_hash(node):
    # TODO: Check this implementation again
    sp.verify(sp.len(node) == 33, "Invalid node")

    return sp.slice(node, 1, 32).open_some()
