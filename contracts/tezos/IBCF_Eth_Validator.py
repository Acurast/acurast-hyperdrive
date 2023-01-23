# --------------------------------------------------------------------------
# This contract validates proofs generated from `eth_getProof` ethereum RPC.
#
# More info: https://eips.ethereum.org/EIPS/eip-1186
# ---------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.IBCF_Aggregator import Type
from contracts.tezos.libs.utils import Bytes, Nat, RLP

HASH_FUNCTION = sp.keccak
EMPTY_TRIE_ROOT_HASH = sp.bytes(
    "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"
)
ACCOUNT_STATE_ROOT_INDEX = 2


class Error:
    NOT_ADMINISTRATOR = "NOT_ADMINISTRATOR"
    NOT_VALIDATOR = "NOT_VALIDATOR"
    UNPROCESSED_BLOCK_STATE = "UNPROCESSED_BLOCK_STATE"
    NO_CONSENSUS_FOR_STATE = "NO_CONSENSUS_FOR_STATE"
    INVALID_SNAPSHOT = "INVALID_SNAPSHOT"


class Type:
    # Views
    Verify_argument = sp.TRecord(
        rlp=sp.TRecord(
            to_list=sp.TLambda(sp.TBytes, sp.TMap(sp.TNat, sp.TBytes)),
            is_list=sp.TLambda(sp.TBytes, sp.TBool),
            remove_offset=sp.TLambda(sp.TBytes, sp.TBytes),
        ).right_comb(),
        proof_rlp=sp.TBytes,
        state_root=sp.TBytes,
        path=sp.TBytes,
    ).right_comb()
    Validate_storage_proof_argument = sp.TRecord(
        account=sp.TBytes,
        block_number=sp.TNat,
        account_proof_rlp=sp.TBytes,
        storage_slot=sp.TBytes,
        storage_proof_rlp=sp.TBytes,
    ).right_comb()
    # Entry points
    Configure_argument = sp.TList(
        sp.TVariant(
            update_administrator=sp.TAddress,
            update_validators=sp.TSet(
                sp.TVariant(add=sp.TAddress, remove=sp.TAddress).right_comb()
            ),
            update_minimum_endorsements=sp.TNat,
            update_history_length=sp.TNat,
            update_snapshot_interval=sp.TNat,
            update_current_snapshot=sp.TNat,
        ).right_comb()
    )
    Submit_account_proof_argument = sp.TRecord(
        account=sp.TBytes,
        block_header=sp.TBytes,
        account_state_proof=sp.TBytes,
    ).right_comb()
    Submit_block_state_root_argument = sp.TRecord(
        block_number=sp.TNat,
        state_root=sp.TBytes,
    ).right_comb()


class Inlined:
    @staticmethod
    def failIfNotAdministrator(self):
        """
        This method when used, ensures that only the administrator is allowed to call a given entrypoint
        """
        sp.verify(self.data.config.administrator == sp.sender, Error.NOT_ADMINISTRATOR)

    @staticmethod
    def failIfNotValidator(self):
        """
        This method when used, ensures that only validators are allowed to call a given entrypoint
        """
        sp.verify(self.data.config.validators.contains(sp.sender), Error.NOT_VALIDATOR)


class Lambdas:
    @staticmethod
    def validate_block_state_root(arg):
        (state_roots, minimum_endorsements) = sp.match_record(
            arg,
            "state_roots",
            "minimum_endorsements",
        )

        endorsements_per_root = sp.local(
            "state_roots", sp.map(tkey=sp.TBytes, tvalue=sp.TNat)
        )
        with sp.for_("entry", state_roots.items()) as entry:
            endorsements_per_root.value[entry.value] = (
                endorsements_per_root.value.get(entry.value, default_value=0) + 1
            )

        state_root = sp.local("state_root", sp.bytes("0x"))
        with sp.for_("root_state", endorsements_per_root.value.keys()) as root_state:
            with sp.if_(
                endorsements_per_root.value[root_state]
                > endorsements_per_root.value.get(state_root.value, default_value=0)
            ):
                state_root.value = root_state

        with sp.if_(
            (sp.len(endorsements_per_root.value) == 0)
            | (endorsements_per_root.value[state_root.value] < minimum_endorsements)
        ):
            # Return None if state root was not endorsed enough
            sp.result(sp.none)
        with sp.else_():
            sp.result(sp.some(state_root.value))

    @staticmethod
    def nibbles_of_bytes(arg):
        """
        Convert bytes to nibbels (e.g. 0xff => 0x0f0f)
        """
        (_bytes, skip_nibbles) = sp.match_record(
            sp.set_type_expr(arg, sp.TRecord(bytes=sp.TBytes, skip=sp.TNat)),
            "bytes",
            "skip",
        )

        nat_of_bytes_lambda = sp.compute(sp.build_lambda(Nat.of_bytes))

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

    @staticmethod
    def shared_prefix_length(arg):
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

    @staticmethod
    def merkle_patricia_compact_decode(_bytes):
        sp.verify(sp.len(_bytes) > 0, "Empty bytes array")

        nat_of_bytes_lambda = sp.compute(sp.build_lambda(Nat.of_bytes))
        nibbles_of_bytes_lambda = sp.compute(sp.build_lambda(Lambdas.nibbles_of_bytes))

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
            nibbles_of_bytes_lambda(sp.record(bytes=_bytes, skip=nibbles_to_skip.value))
        )

    @staticmethod
    def extract_nibble(arg):
        """
        Nibble is extracted as the least significant nibble in the returned byte
        """
        (path, position) = sp.match_record(
            sp.set_type_expr(arg, sp.TRecord(path=sp.TBytes, position=sp.TNat)),
            "path",
            "position",
        )

        nat_of_bytes_lambda = sp.compute(sp.build_lambda(Nat.of_bytes))

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

    @staticmethod
    def verify(arg):
        (rlp, proof_rlp, state_root, path32) = sp.match_record(
            sp.set_type_expr(
                arg,
                Type.Verify_argument,
            ),
            "rlp",
            "proof_rlp",
            "state_root",
            "path",
        )

        nibbles_of_bytes_lambda = sp.compute(sp.build_lambda(Lambdas.nibbles_of_bytes))
        shared_prefix_length_lambda = sp.compute(
            sp.build_lambda(Lambdas.shared_prefix_length)
        )
        merkle_patricia_compact_decode_lambda = sp.compute(
            sp.build_lambda(Lambdas.merkle_patricia_compact_decode)
        )
        extract_nibble_lambda = sp.compute(sp.build_lambda(Lambdas.extract_nibble))

        proof_nodes = sp.compute(rlp.to_list(proof_rlp))

        proof_nodes_length = sp.compute(sp.len(proof_nodes))
        path = sp.compute(
            nibbles_of_bytes_lambda(sp.record(bytes=path32, skip=sp.nat(0)))
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
                            merkle_patricia_compact_decode_lambda(
                                rlp.remove_offset(nodes[0])
                            )
                        )
                        path_offset.value += sp.compute(
                            shared_prefix_length_lambda(
                                sp.record(
                                    path_offset=path_offset.value,
                                    full_path=path,
                                    path=node_path,
                                )
                            )
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
                                next_hash.value = sp.compute(
                                    get_next_hash(rlp.remove_offset(children))
                                )

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
                                    extract_nibble_lambda(
                                        sp.record(
                                            position=path_offset.value, path=path32
                                        )
                                    )
                                )

                                children = nodes[node_index]

                                # Ensure that the next path item is empty, end of exclusion proof
                                sp.verify(
                                    sp.len(rlp.remove_offset(nodes[node_index])) == 0,
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
                                extract_nibble_lambda(
                                    sp.record(position=path_offset.value, path=path32)
                                )
                            )

                            children = sp.compute(nodes[node_index])

                            # advance by one
                            path_offset.value += 1

                            # not last level
                            with sp.if_(rlp.is_list(children)):
                                next_hash.value = HASH_FUNCTION(children)
                            with sp.else_():
                                next_hash.value = sp.compute(
                                    get_next_hash(rlp.remove_offset(children))
                                )

            sp.result(result.value)


class RLP_utils:
    @staticmethod
    def to_list():
        return sp.compute(sp.build_lambda(RLP.Decoder.decode_list))

    @staticmethod
    def is_list():
        return sp.compute(sp.build_lambda(RLP.Decoder.is_list))

    @staticmethod
    def remove_offset():
        return sp.compute(sp.build_lambda(RLP.Decoder.without_length_prefix))


class IBCF_Eth_Validator(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                config=sp.TRecord(
                    # Multi-sig address allowed to manage the contract
                    administrator=sp.TAddress,
                    # Validators
                    validators=sp.TSet(sp.TAddress),
                    # Minimum expected endorsements for a given state root to be considered valid
                    minimum_endorsements=sp.TNat,
                    # The validator only stores the state roots of the latest `history_length` blocks
                    history_length=sp.TNat,
                    # Number of blocks between each snapshot
                    snapshot_interval=sp.TNat,
                ),
                current_snapshot=sp.TNat,
                state_root=sp.TBigMap(sp.TNat, sp.TMap(sp.TAddress, sp.TBytes)),
                history=sp.TSet(sp.TNat),
            )
        )

    @sp.entry_point(parameter_type=Type.Submit_block_state_root_argument)
    def submit_block_state_root(self, arg):
        (block_number, state_root) = sp.match_record(
            arg,
            "block_number",
            "state_root",
        )

        # Check if sender is a validator
        Inlined.failIfNotValidator(self)

        # Make sure the snapshots are submitted sequencially
        with sp.if_(self.data.current_snapshot == 0):
            self.data.current_snapshot = block_number
        with sp.else_():
            sp.verify(
                self.data.current_snapshot == block_number, Error.INVALID_SNAPSHOT
            )

        # Store the block state root
        with sp.if_(self.data.state_root.contains(block_number)):
            self.data.state_root[block_number][sp.sender] = state_root
        with sp.else_():
            self.data.state_root[block_number] = sp.map({sp.sender: state_root})

        # Finalize snapshot if consensus has been reached
        block_state_roots = sp.compute(
            self.data.state_root.get(
                block_number, message=Error.UNPROCESSED_BLOCK_STATE
            )
        )
        can_finalize_snapshot = sp.compute(
            sp.build_lambda(Lambdas.validate_block_state_root)(
                sp.record(
                    state_roots=block_state_roots,
                    minimum_endorsements=self.data.config.minimum_endorsements,
                )
            ).is_some()
        )
        with sp.if_(can_finalize_snapshot):
            self.data.current_snapshot += self.data.config.snapshot_interval
            self.data.history.add(block_number)

            # Remove old root states
            with sp.if_(sp.len(self.data.history) > self.data.config.history_length):
                oldest = sp.local("oldest", block_number)
                with sp.for_("block", self.data.history.elements()) as b:
                    with sp.if_(b < oldest.value):
                        oldest.value = b

                del self.data.state_root[oldest.value]
                self.data.history.remove(oldest.value)

    @sp.entry_point(parameter_type=Type.Configure_argument)
    def configure(self, actions):

        # Only allowed addresses can call this entry point
        Inlined.failIfNotAdministrator(self)

        with sp.for_("action", actions) as action:
            with action.match_cases() as action:
                with action.match("update_validators") as payload:
                    with sp.for_("el", payload.elements()) as el:
                        with el.match_cases() as cases:
                            with cases.match("add") as add:
                                self.data.config.validators.add(add)
                            with cases.match("remove") as remove:
                                self.data.config.validators.remove(remove)
                with action.match("update_administrator") as administrator:
                    self.data.config.administrator = administrator
                with cases.match("update_minimum_endorsements") as payload:
                    self.data.config.minimum_endorsements = payload
                with cases.match("update_history_length") as payload:
                    self.data.config.history_length = payload
                with cases.match("update_snapshot_interval") as payload:
                    self.data.config.snapshot_interval = payload
                with cases.match("update_current_snapshot") as payload:
                    self.data.current_snapshot = payload

    @sp.onchain_view()
    def validate_storage_proof(self, arg):
        (
            account,
            block_number,
            account_proof_rlp,
            storage_slot,
            storage_proof_rlp,
        ) = sp.match_record(
            sp.set_type_expr(
                arg,
                Type.Validate_storage_proof_argument,
            ),
            "account",
            "block_number",
            "account_proof_rlp",
            "storage_slot",
            "storage_proof_rlp",
        )

        verify_lambda = sp.compute(sp.build_lambda(Lambdas.verify))

        block_state_roots = sp.compute(
            self.data.state_root.get(
                block_number, message=Error.UNPROCESSED_BLOCK_STATE
            )
        )
        validate_block_state_root = sp.build_lambda(Lambdas.validate_block_state_root)
        state_root = sp.compute(
            validate_block_state_root(
                sp.record(
                    state_roots=block_state_roots,
                    minimum_endorsements=self.data.config.minimum_endorsements,
                )
            ).open_some(Error.NO_CONSENSUS_FOR_STATE)
        )

        rlp = sp.record(
            to_list=RLP_utils.to_list(),
            is_list=RLP_utils.is_list(),
            remove_offset=RLP_utils.remove_offset(),
        )

        # The path to the account state is the hash of the contract address
        account_state_path = HASH_FUNCTION(account)

        # Validate proof and extract the account state
        account_state_root = sp.compute(
            rlp.remove_offset(
                rlp.to_list(
                    verify_lambda(
                        sp.set_type_expr(
                            sp.record(
                                path=account_state_path,
                                proof_rlp=account_proof_rlp,
                                rlp=rlp,
                                state_root=state_root,
                            ),
                            Type.Verify_argument,
                        )
                    )
                )[ACCOUNT_STATE_ROOT_INDEX]
            )
        )

        # The path to the contract state is the hash of the storage slot
        storage_state_path = HASH_FUNCTION(storage_slot)

        sp.result(
            verify_lambda(
                sp.set_type_expr(
                    sp.record(
                        rlp=rlp,
                        proof_rlp=storage_proof_rlp,
                        state_root=account_state_root,
                        path=storage_state_path,
                    ),
                    Type.Verify_argument,
                )
            )
        )


def get_next_hash(node):
    sp.verify(sp.len(node) == 32, "Invalid node")

    return node
