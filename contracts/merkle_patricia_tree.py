import smartpy as sp

from contracts.utils.misc import chop_first_bit, split_common_prefix, remove_prefix
from contracts.utils.bytes import bits_of_bytes

HASH_FUNCTION = sp.blake2b
HASH_LENGTH = 256
NULL_HASH = sp.bytes("0x")

# This constant is used to limit the data length being inserted.
MAX_VALUE_LENGTH = 1000
# This constant is used to limit the amount of states being stored per merkle tree.
MAX_STATES = 200


def ENCODE(d):
    return sp.pack(d)


class Error:
    PROOF_INVALID = "PROOF_INVALID"
    NOT_FOUND = "NOT_FOUND"
    NOT_ALLOWED = "NOT_ALLOWED"
    STATE_TOO_LARGE = "STATE_TOO_LARGE"


#################
# Inlined methods
#################


def hash_state(owner, key, value):
    return HASH_FUNCTION(sp.concat([owner, key, value]))


def hash_key(owner, key):
    return HASH_FUNCTION(sp.concat([owner, key]))


def hash_edge(edge):
    # return HASH_FUNCTION(edge.node + sp.pack(edge.label))
    return edge.node


def hash_node(node):
    return HASH_FUNCTION(hash_edge(node.children[0]) + hash_edge(node.children[1]))


def insert_node(self, node):
    node_hash = hash_node(node)
    self.data.tree.nodes[node_hash] = node

    return node_hash


def replace_node(self, old_hash, node):
    del self.data.tree.nodes[old_hash]
    return insert_node(self, node)


class Type:
    Label = sp.TRecord(data=sp.TString, length=sp.TNat).right_comb()
    Edge = sp.TRecord(node=sp.TBytes, label=Label).right_comb()
    Node = sp.TRecord(children=sp.TMap(sp.TInt, Edge)).right_comb()
    Tree = sp.TRecord(
        root=sp.TBytes,
        root_edge=Edge,
        nodes=sp.TMap(sp.TBytes, Node),
        states=sp.TMap(sp.TBytes, sp.TBytes),
    ).right_comb()
    State = sp.TRecord(
        owner=sp.TBytes,
        key=sp.TBytes,
        value=sp.TBytes,
    ).right_comb()
    VerifyProofArgument = sp.TRecord(
        level=sp.TNat, proof=sp.TList(sp.TOr(sp.TBytes, sp.TBytes)), state=State
    ).right_comb()
    InsertArgument = sp.TRecord(key=sp.TBytes, value=sp.TBytes).right_comb()
    # Views
    GetProofArgument = sp.TRecord(
        owner=sp.TAddress, level=sp.TNat, key=sp.TBytes
    ).right_comb()
    ProofResult = sp.TRecord(
        level=sp.TNat,
        merkle_root=sp.TBytes,
        proof=sp.TList(sp.TOr(sp.TBytes, sp.TBytes)),
    ).right_comb()


EMPTY_TREE = sp.record(
    root=sp.bytes("0x"),
    root_edge=sp.record(
        node=sp.bytes("0x"),
        label=sp.record(data="", length=sp.nat(0)),
    ),
    nodes=sp.map(tkey=sp.TBytes, tvalue=Type.Node),
    states=sp.map(tkey=sp.TBytes, tvalue=sp.TBytes),
)


class IBCF(sp.Contract):
    """
    Inter blockchain communication framework contract
    """

    def __init__(self):
        self.init_type(
            sp.TRecord(
                bytes_to_bits=sp.TMap(sp.TBytes, sp.TString),
                administrators=sp.TSet(sp.TAddress),
                merkle_history=sp.TBigMap(sp.TNat, Type.Tree),
                tree=Type.Tree,
            ).right_comb()
        )

    @sp.private_lambda(with_storage="read-write", with_operations=False, wrap_call=True)
    def insert_at_edge(self, arg):
        with sp.set_result_type(Type.Edge):
            r_stack = sp.local("r_stack", sp.map(tkey=sp.TInt, tvalue=Type.Edge))
            r_size = sp.local("r_size", sp.int(0))

            c_stack = sp.local(
                "c_stack",
                sp.map(
                    {
                        1: sp.record(
                            edge=arg.edge,
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
                        key=Type.Label,
                        value=sp.TBytes,
                        prefix=sp.TOption(Type.Label),
                        node=sp.TOption(Type.Node),
                        head=sp.TOption(sp.TInt),
                        edge_node=sp.TOption(sp.TBytes),
                    ),
                ),
            )
            c_size = sp.local("c_size", sp.int(1))
            first = sp.local("first", True)

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

                    result = r_stack.value[r_size.value]
                    n = sp.local("n", node.open_some())
                    n.value.children[head.open_some()] = result

                    new_node_hash = replace_node(self, edge_node.open_some(), n.value)

                    r_stack.value[r_size.value] = sp.record(
                        node=new_node_hash, label=prefix.open_some()
                    )
                with sp.else_():
                    sp.verify(key.length >= edge.label.length, "Key length mismatch")
                    (prefix, suffix) = sp.match_record(
                        split_common_prefix(key.data, edge.label.data),
                        "prefix",
                        "suffix",
                    )

                    new_node_hash = sp.bind_block()
                    with new_node_hash:
                        with sp.if_(suffix.length == 0):
                            # Full match with the key, update operation
                            r_size.value += 1
                            r_stack.value[r_size.value] = sp.record(
                                node=value, label=prefix
                            )
                        with sp.else_():
                            with sp.if_(prefix.length < edge.label.length):
                                # Mismatch, so lets create a new branch node.
                                (head, tail) = sp.match_pair(chop_first_bit(suffix))
                                branch_node = sp.local("node", sp.record(children={}))

                                branch_node.value.children[head] = sp.record(
                                    node=value, label=tail
                                )
                                branch_node.value.children[1 - head] = sp.record(
                                    node=edge.node,
                                    label=remove_prefix(edge.label, prefix.length + 1),
                                )

                                r_size.value += 1
                                r_stack.value[r_size.value] = sp.record(
                                    node=insert_node(self, branch_node.value),
                                    label=prefix,
                                )

                            with sp.else_():
                                # Partial match, lets just follow the path
                                sp.verify(suffix.length > 1, "Bad key")

                                (head, tail) = sp.match_pair(chop_first_bit(suffix))
                                node = sp.compute(self.data.tree.nodes[edge.node])

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

            sp.result(r_stack.value[r_size.value])

    @sp.entry_point()
    def snapshot_merkle_tree(self):
        # Only allowed addresses can call this entry point
        sp.verify(self.data.administrators.contains(sp.sender), Error.NOT_ALLOWED)

        self.data.merkle_history[sp.level] = self.data.tree
        self.data.tree = EMPTY_TREE

    @sp.entry_point()
    def insert(self, param):
        """
        Include new state into the merkle tree.
        """
        sp.set_type(param, Type.InsertArgument)

        # Do not allow users to insert values bigger than MAX_VALUE_LENGTH
        sp.verify(sp.len(param.value) < MAX_VALUE_LENGTH, Error.STATE_TOO_LARGE)

        key_label = sp.record(
            data=bits_of_bytes(self, hash_key(ENCODE(sp.sender), param.key)),
            length=HASH_LENGTH,
        )

        # Set new state
        state_hash = sp.compute(hash_state(ENCODE(sp.sender), param.key, param.value))
        self.data.tree.states[state_hash] = param.value

        edge = sp.local("edge", sp.record(label=key_label, node=state_hash))
        # Skip first insertion
        with sp.if_(self.data.tree.root != NULL_HASH):
            edge.value = self.insert_at_edge(
                sp.record(
                    edge=self.data.tree.root_edge, key=key_label, value=state_hash
                )
            )

        self.data.tree.root = hash_edge(edge.value)
        self.data.tree.root_edge = edge.value

    @sp.onchain_view()
    def get_proof(self, arg):
        """
        Returns the Merkle-proof for the given key

        :returns: sp.TRecord(
            root_hash   = sp.TBytes,
            proof       = sp.TList(sp.TOr(sp.TBytes, sp.TBytes))
        )
        """
        sp.set_type(arg, Type.GetProofArgument)
        key_label = sp.local(
            "key_label",
            sp.record(
                data=bits_of_bytes(self, hash_key(ENCODE(arg.owner), arg.key)),
                length=HASH_LENGTH,
            ),
        )

        tree = sp.local("tree", self.data.merkle_history[arg.level])
        root_edge = sp.local("root_edge", tree.value.root_edge)
        blinded_path = sp.local("blinded_path", [])

        continue_loop = sp.local("continue_loop", True)
        with sp.while_(continue_loop.value):
            (prefix, suffix) = sp.match_record(
                split_common_prefix(key_label.value.data, root_edge.value.label.data),
                "prefix",
                "suffix",
            )
            sp.verify(prefix.length == root_edge.value.label.length, Error.NOT_FOUND)

            with sp.if_(suffix.length == 0):
                # Proof found
                continue_loop.value = False
            with sp.else_():
                (head, tail) = sp.match_pair(chop_first_bit(suffix))

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
                with sp.if_(head == 0):
                    h = hash_edge(tree.value.nodes[root_edge.value.node].children[1])
                    blinded_path.value.push(sp.right(h))
                with sp.else_():
                    h = hash_edge(tree.value.nodes[root_edge.value.node].children[0])
                    blinded_path.value.push(sp.left(h))

                root_edge.value = tree.value.nodes[root_edge.value.node].children[head]
                key_label.value = tail

        with sp.set_result_type(Type.ProofResult):
            sp.result(
                sp.record(
                    level=arg.level,
                    merkle_root=tree.value.root,
                    proof=blinded_path.value,
                )
            )

    @sp.entry_point()
    def verify_proof(self, arg):
        """
        Validates a proof against a given state.
        """
        sp.set_type(arg, Type.VerifyProofArgument)

        state_hash = hash_state(arg.state.owner, arg.state.key, arg.state.value)
        derived_hash = sp.local("derived_hash", state_hash)
        with sp.for_("el", arg.proof) as el:
            with el.match_cases() as cases:
                with cases.match("Left") as left:
                    derived_hash.value = HASH_FUNCTION(left + derived_hash.value)
                with cases.match("Right") as right:
                    derived_hash.value = HASH_FUNCTION(derived_hash.value + right)

        sp.verify(
            self.data.merkle_history[arg.level].root == derived_hash.value,
            Error.PROOF_INVALID,
        )
