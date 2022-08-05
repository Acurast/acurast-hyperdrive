# --------------------------------------------------------------------------
# This implements a merkle tree to aggregate user provided states cheaply
# and generates proofs that can be validated in the Ethereum blockchain.
# ---------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.utils.misc import (
    chop_first_bit,
    split_common_prefix,
    remove_prefix,
)
from contracts.tezos.utils.bytes import bits_of_bytes, int_of_bits

HASH_FUNCTION = sp.keccak
HASH_LENGTH = 256
NULL_HASH = sp.bytes("0x")

# This constant is used to limit the data length being inserted.
MAX_STATE_LENGTH = 32
# This constant is used to limit the amount of states being stored per merkle tree.
MAX_STATES = 10

EMPTY_TREE = sp.record(
    root=sp.bytes("0x"),
    root_edge=sp.record(
        node=sp.bytes("0x"),
        key=sp.record(data=0, length=0),
    ),
    nodes=sp.map(),
    states=sp.map(),
    signatures=sp.map(),
)


def ENCODE(d):
    return sp.pack(d)


class Error:
    PROOF_INVALID = "PROOF_INVALID"
    NOT_FOUND = "NOT_FOUND"
    NOT_ADMINISTRATOR = "NOT_ADMINISTRATOR"
    STATE_TOO_LARGE = "STATE_TOO_LARGE"
    LEVEL_ALREADY_USED = "LEVEL_ALREADY_USED"
    TOO_MANY_STATES = "TOO_MANY_STATES"
    NOT_SIGNER = "NOT_SIGNER"
    UNPROCESSED_BLOCK_STATE = "UNPROCESSED_BLOCK_STATE"


#################
# Inlined methods
#################


def hash_state(owner, key, value):
    return HASH_FUNCTION(sp.concat([owner, key, value]))


def hash_key(owner, key):
    return HASH_FUNCTION(sp.concat([owner, key]))


def hash_edge(edge):
    # return HASH_FUNCTION(edge.node + sp.pack(edge.key))
    return edge.node


def hash_node(node):
    return HASH_FUNCTION(hash_edge(node.children[0]) + hash_edge(node.children[1]))


def insert_node(tree, node):
    node_hash = hash_node(node)
    tree.value.nodes[node_hash] = node

    return node_hash


def replace_node(tree, old_hash, node):
    del tree.value.nodes[old_hash]
    return insert_node(tree, node)

class Inlined:
    @staticmethod
    def failIfNotAdministrator(self):
        """
        This method when used, ensures that only the administrator is allowed to call a given entrypoint
        """
        sp.verify(self.data.config.administrator == sp.sender, Error.NOT_ADMINISTRATOR)

    @staticmethod
    def failIfNotSigner(self):
        """
        This method when used, ensures that only signers are allowed to call a given entrypoint
        """
        sp.verify(self.data.config.signers.contains(sp.sender), Error.NOT_SIGNER)

class Type:
    KeyMeta = sp.TRecord(data=sp.TNat, length=sp.TNat).right_comb()
    Edge = sp.TRecord(node=sp.TBytes, key=KeyMeta).right_comb()
    Node = sp.TRecord(children=sp.TMap(sp.TInt, Edge)).right_comb()
    State = sp.TRecord(
        owner=sp.TBytes,
        key=sp.TBytes,
        value=sp.TBytes,
    ).right_comb()
    Signature = sp.TRecord(
        r=sp.TBytes,
        s=sp.TBytes,
    ).right_comb()
    Tree = sp.TRecord(
        root=sp.TBytes,
        root_edge=Edge,
        nodes=sp.TMap(sp.TBytes, Node),
        states=sp.TMap(sp.TBytes, sp.TBytes),
        signatures=sp.TMap(sp.TAddress, Signature),
    ).right_comb()

    # Entry points
    Insert_argument = sp.TRecord(key=sp.TBytes, value=sp.TBytes).right_comb()
    Submit_signature = sp.TRecord(level=sp.TNat, signature=Signature).right_comb()
    Configure_argument = sp.TVariant(
        update_administrator=sp.TAddress,
        update_signers=sp.TSet(
            sp.TVariant(add=sp.TAddress, remove=sp.TAddress).right_comb()
        ),
        update_history_ttl=sp.TNat,
        update_max_state_size=sp.TNat,
        update_max_states=sp.TNat,
    ).right_comb()

    # Views
    Get_proof_argument = sp.TRecord(
        owner=sp.TAddress, level=sp.TNat, key=sp.TBytes
    ).right_comb()
    Proof_result = sp.TRecord(
        level=sp.TNat,
        merkle_root=sp.TBytes,
        key=sp.TBytes,
        value=sp.TBytes,
        proof=sp.TList(sp.TOr(sp.TBytes, sp.TBytes)),
        signatures=sp.TMap(sp.TAddress, Signature),
    ).right_comb()
    Verify_proof_argument = sp.TRecord(
        level=sp.TNat, proof=sp.TList(sp.TOr(sp.TBytes, sp.TBytes)), state=State
    ).right_comb()


class IBCF_Aggregator(sp.Contract):
    """
    Inter blockchain communication framework contract
    """

    def __init__(self):
        self.init_type(
            sp.TRecord(
                config=sp.TRecord(
                    # Multi-sig address allowed to manage the contract
                    administrator=sp.TAddress,
                    # State signers
                    signers=sp.TSet(sp.TAddress),
                    # This constant sets a time to live for every entry in merkle_history
                    history_ttl=sp.TNat,
                    # This constant is used to limit the data length being inserted (in bytes).
                    max_state_size=sp.TNat,
                    # This constant is used to limit the amount of states being stored per merkle tree.
                    max_states=sp.TNat,
                ),
                bytes_to_bits=sp.TMap(sp.TBytes, sp.TString),
                merkle_history=sp.TBigMap(sp.TNat, Type.Tree),
                merkle_history_indexes=sp.TList(sp.TNat),
            ).right_comb()
        )

    @sp.private_lambda(with_storage="read-write", with_operations=False, wrap_call=True)
    def insert_at_edge(self, arg):
        tree = sp.local("tree", arg.tree)
        with sp.set_result_type(Type.Tree):
            # Michelson does not have recursive calls
            r_size = sp.local("r_size", sp.int(0))
            r_stack = sp.local("r_stack", sp.map(tkey=sp.TInt, tvalue=Type.Edge))
            c_size = sp.local("c_size", sp.int(1))
            c_stack = sp.local(
                "c_stack",
                sp.map(
                    {
                        1: sp.record(
                            edge=tree.value.root_edge,
                            key=arg.key,
                            value=arg.value,
                            prefix=sp.none,
                            node=sp.none,
                            head=sp.none,
                            edge_node=sp.none,
                        )
                    },
                    tkey=sp.TInt,
                    tvalue=sp.TRecord(
                        edge=Type.Edge,
                        key=Type.KeyMeta,
                        value=sp.TBytes,
                        prefix=sp.TOption(Type.KeyMeta),
                        node=sp.TOption(Type.Node),
                        head=sp.TOption(sp.TInt),
                        edge_node=sp.TOption(sp.TBytes),
                    ),
                ),
            )
            first = sp.local("first", True)

            chop_first_bit_lambda = sp.compute(sp.build_lambda(chop_first_bit))
            remove_prefix_lambda = sp.compute(sp.build_lambda(remove_prefix))
            split_common_prefix_lambda = sp.compute(
                sp.build_lambda(split_common_prefix)
            )

            with sp.while_(c_size.value > 0):
                (edge, key, value, node, head, edge_node, prefix) = sp.match_record(
                    c_stack.value[c_size.value],
                    "edge",
                    "key",
                    "value",
                    "node",
                    "head",
                    "edge_node",
                    "prefix",
                )

                with sp.if_(first.value):
                    first.value = False
                    c_size.value = 0
                    c_stack.value = {}

                with sp.if_((r_size.value > 0) & (c_size.value > 0)):
                    del c_stack.value[c_size.value]
                    c_size.value -= 1

                    n = sp.local("n", node.open_some())
                    n.value.children[head.open_some()] = r_stack.value[r_size.value]

                    new_node_hash = replace_node(tree, edge_node.open_some(), n.value)

                    r_stack.value[r_size.value] = sp.compute(
                        sp.record(node=new_node_hash, key=prefix.open_some())
                    )
                with sp.else_():
                    sp.verify(key.length >= edge.key.length, "KEY_LENGTH_MISMATCH")
                    (prefix, suffix) = sp.match_record(
                        split_common_prefix_lambda((key, edge.key)),
                        "prefix",
                        "suffix",
                    )

                    new_node_hash = sp.bind_block()
                    with new_node_hash:
                        with sp.if_(suffix.length == 0):
                            # Full match with the key, update operation
                            r_size.value += 1
                            r_stack.value[r_size.value] = sp.record(
                                node=value, key=prefix
                            )
                        with sp.else_():
                            with sp.if_(prefix.length < edge.key.length):
                                # Mismatch, so lets create a new branch node.
                                (head, tail) = sp.match_pair(
                                    chop_first_bit_lambda(suffix)
                                )
                                branch_node = sp.local(
                                    "node",
                                    sp.record(
                                        children={
                                            head: sp.record(node=value, key=tail),
                                            (1 - head): sp.record(
                                                node=edge.node,
                                                key=remove_prefix_lambda(
                                                    (edge.key, prefix.length + 1)
                                                ),
                                            ),
                                        }
                                    ),
                                )

                                r_size.value += 1
                                r_stack.value[r_size.value] = sp.compute(
                                    sp.record(
                                        node=insert_node(tree, branch_node.value),
                                        key=prefix,
                                    )
                                )

                            with sp.else_():
                                # Partial match, lets just follow the path
                                sp.verify(suffix.length > 1, "BAD_SUFFIX")

                                (head, tail) = sp.match_pair(
                                    chop_first_bit_lambda(suffix)
                                )
                                node = sp.compute(tree.value.nodes[edge.node])

                                c_size.value += 1
                                c_stack.value[c_size.value] = sp.record(
                                    edge=node.children[head],
                                    key=tail,
                                    value=value,
                                    prefix=sp.some(prefix),
                                    node=sp.some(node),
                                    head=sp.some(head),
                                    edge_node=sp.some(edge.node),
                                )

            # Update root node
            edge = sp.compute(r_stack.value[r_size.value])
            tree.value.root = hash_edge(edge)
            tree.value.root_edge = edge

            sp.result(tree.value)

    @sp.entry_point(parameter_type = Type.Insert_argument)
    def insert(self, param):
        """
        Include new state into the merkle tree.
        """
        int_of_bits_lambda = sp.compute(sp.build_lambda(int_of_bits))

        with sp.if_(~self.data.merkle_history.contains(sp.level)):
            self.data.merkle_history[sp.level] = EMPTY_TREE

        tree = sp.local("tree", self.data.merkle_history[sp.level])

        # Do not allow users to insert values bigger than max_state_size
        sp.verify(
            sp.len(param.value) <= self.data.config.max_state_size,
            Error.STATE_TOO_LARGE,
        )
        sp.verify(sp.len(tree.value.states) < MAX_STATES, Error.TOO_MANY_STATES)

        latest_indexes = sp.local("latest_indexes", [])
        with sp.for_("el", self.data.merkle_history_indexes) as el:
            with sp.if_(
                (el + self.data.config.history_ttl > sp.level) & (el != sp.level)
            ):
                latest_indexes.value.push(el)
            with sp.else_():
                # Remove old merkle tree
                del self.data.merkle_history[el]

        self.data.merkle_history_indexes = latest_indexes.value
        self.data.merkle_history_indexes.push(sp.level)

        key_hash = sp.compute(hash_key(ENCODE(sp.sender), param.key))
        key = sp.compute(
            sp.record(
                data=int_of_bits_lambda(
                    bits_of_bytes(
                        self.data.bytes_to_bits, key_hash
                    )
                ),
                length=HASH_LENGTH,
            )
        )

        # Set new state
        tree.value.states[key_hash] = param.value

        state_hash = sp.compute(hash_state(ENCODE(sp.sender), param.key, param.value))
        with sp.if_(tree.value.root != NULL_HASH):
            # Skip on first insertion
            tree.value = self.insert_at_edge(
                sp.record(tree=tree.value, key=key, value=state_hash)
            )
        with sp.else_():
            edge = sp.compute(sp.record(key=key, node=state_hash))
            tree.value.root = hash_edge(edge)
            tree.value.root_edge = edge

        self.data.merkle_history[sp.level] = tree.value

    @sp.entry_point(parameter_type=Type.Submit_signature)
    def submit_signature(self, param):
        # Only allowed addresses can call this entry point
        Inlined.failIfNotSigner(self)

        with sp.if_(self.data.merkle_history.contains(param.level)):
            self.data.merkle_history[param.level].signatures[sp.sender] = param.signature
        with sp.else_():
            sp.failwith(Error.UNPROCESSED_BLOCK_STATE)

    @sp.entry_point(parameter_type=Type.Configure_argument)
    def configure(self, param):
        # Only allowed addresses can call this entry point
        Inlined.failIfNotAdministrator(self)

        with param.match_cases() as action:
            with action.match("update_signers") as payload:
                with sp.for_("el", payload.elements()) as el:
                    with el.match_cases() as cases:
                        with cases.match("add") as add:
                            self.data.config.signers.add(add)
                        with cases.match("remove") as remove:
                            self.data.config.signers.remove(remove)
            with action.match("update_administrator") as administrator:
                self.data.config.administrator = administrator
            with cases.match("update_history_ttl") as payload:
                self.data.config.history_ttl = payload
            with cases.match("update_max_state_size") as payload:
                self.data.config.max_state_size = payload
            with cases.match("update_max_states") as payload:
                self.data.config.max_states = payload

    @sp.onchain_view()
    def get_proof(self, arg):
        """
        Returns the Merkle-proof for the given key

        :returns: sp.TRecord(
            level       = sp.TNat,
            key         = sp.TBytes,
            value       = sp.TBytes,
            merkle_root = sp.TBytes,
            proof       = sp.TList(sp.TOr(sp.TBytes, sp.TBytes))
        )
        """
        sp.set_type(arg, Type.Get_proof_argument)

        chop_first_bit_lambda = sp.compute(sp.build_lambda(chop_first_bit))
        split_common_prefix_lambda = sp.compute(sp.build_lambda(split_common_prefix))
        int_of_bits_lambda = sp.compute(sp.build_lambda(int_of_bits))

        key_hash = sp.compute(hash_key(ENCODE(arg.owner), arg.key))
        key = sp.local(
            "key",
            sp.record(
                data=int_of_bits_lambda(
                    bits_of_bytes(
                        self.data.bytes_to_bits, key_hash
                    )
                ),
                length=HASH_LENGTH,
            ),
        )

        tree = sp.local("tree", self.data.merkle_history[arg.level])
        root_edge = sp.local("root_edge", tree.value.root_edge)
        blinded_path = sp.local("blinded_path", [])

        continue_loop = sp.local("continue_loop", True)
        with sp.while_(continue_loop.value):
            (prefix, suffix) = sp.match_record(
                split_common_prefix_lambda((key.value, root_edge.value.key)),
                "prefix",
                "suffix",
            )
            sp.verify(prefix.length == root_edge.value.key.length, Error.NOT_FOUND)

            with sp.if_(suffix.length == 0):
                # Proof found
                continue_loop.value = False
            with sp.else_():
                (head, tail) = sp.match_pair(chop_first_bit_lambda(suffix))

                # Add hash to proof path with direction (0=left or 1=right)
                #
                # For head = 0
                #
                #      h(a+b)
                #       /   \
                #    0 /     \ 1
                #   h(a)    h(b)
                #    |        |
                #   head    complement
                #
                # The proof path must include the complement, since
                # the head is already known.
                hash = sp.bind_block()
                with hash:
                    with sp.if_(head == 0):
                        sp.result(
                            sp.right(
                                hash_edge(
                                    tree.value.nodes[root_edge.value.node].children[1]
                                )
                            )
                        )
                    with sp.else_():
                        sp.result(
                            sp.left(
                                hash_edge(
                                    tree.value.nodes[root_edge.value.node].children[0]
                                )
                            )
                        )

                blinded_path.value.push(hash.value)
                root_edge.value = tree.value.nodes[root_edge.value.node].children[head]
                key.value = tail

        with sp.set_result_type(Type.Proof_result):
            sp.result(
                sp.record(
                    level=arg.level,
                    key=arg.key,
                    value=tree.value.states[key_hash],
                    merkle_root=tree.value.root,
                    proof=blinded_path.value,
                    signatures=tree.value.signatures,
                )
            )

    @sp.onchain_view()
    def verify_proof(self, arg):
        """
        Validates a proof against a given state.
        """
        sp.set_type(arg, Type.Verify_proof_argument)

        state_hash = hash_state(arg.state.owner, arg.state.key, arg.state.value)
        derived_hash = sp.local("derived_hash", state_hash)
        with sp.for_("el", arg.proof) as el:
            with el.match_cases() as cases:
                with cases.match("Left") as left:
                    derived_hash.value = HASH_FUNCTION(left + derived_hash.value)
                with cases.match("Right") as right:
                    derived_hash.value = HASH_FUNCTION(derived_hash.value + right)

        sp.verify(
            self.data.merkle_history.contains(arg.level)
            & (self.data.merkle_history[arg.level].root == derived_hash.value),
            Error.PROOF_INVALID,
        )
