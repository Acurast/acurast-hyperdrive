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
from contracts.tezos.utils.nat import Nat

HASH_FUNCTION = sp.keccak
HASH_LENGTH = 256
NULL_HASH = sp.bytes("0x")

EMPTY_TREE = sp.record(
    root=sp.bytes("0x"),
    root_edge=sp.record(
        node=sp.bytes("0x"),
        key=sp.record(data=0, length=0),
    ),
    nodes=sp.map(),
    states=sp.map()
)


def ENCODE(d):
    return sp.pack(d)


class Error:
    PROOF_INVALID = "PROOF_INVALID"
    PROOF_NOT_FOUND = "PROOF_NOT_FOUND"
    NOT_ADMINISTRATOR = "NOT_ADMINISTRATOR"
    STATE_TOO_LARGE = "STATE_TOO_LARGE"
    LEVEL_ALREADY_USED = "LEVEL_ALREADY_USED"
    UNPROCESSED_BLOCK_STATE = "UNPROCESSED_BLOCK_STATE"
    CANNOT_SNAPSHOT = "CANNOT_SNAPSHOT"


class Inlined:
    @staticmethod
    def hash_state(owner, key, value):
        return sp.compute(HASH_FUNCTION(sp.concat([owner, key, value])))

    @staticmethod
    def hash_key(owner, key):
        return sp.compute(HASH_FUNCTION(sp.concat([owner, key])))

    @staticmethod
    def hash_edge(edge):
        # return HASH_FUNCTION(edge.node + sp.pack(edge.key))
        return edge.node

    @staticmethod
    def hash_node(node):
        return sp.compute(
            HASH_FUNCTION(
                Inlined.hash_edge(node.children[0])
                + Inlined.hash_edge(node.children[1])
            )
        )

    @staticmethod
    def insert_node(tree, node):
        node_hash = Inlined.hash_node(node)
        tree.value.nodes[node_hash] = node

        return node_hash

    @staticmethod
    def replace_node(tree, old_hash, node):
        del tree.value.nodes[old_hash]
        return Inlined.insert_node(tree, node)

    @staticmethod
    def failIfNotAdministrator(self):
        """
        This method when used, ensures that only the administrator is allowed to call a given entrypoint
        """
        sp.verify(self.data.config.administrator == sp.sender, Error.NOT_ADMINISTRATOR)


class Type:
    KeyMeta = sp.TRecord(data=sp.TNat, length=sp.TNat).right_comb()
    Edge = sp.TRecord(node=sp.TBytes, key=KeyMeta).right_comb()
    Node = sp.TRecord(children=sp.TMap(sp.TInt, Edge)).right_comb()
    State = sp.TRecord(
        owner=sp.TBytes,
        key=sp.TBytes,
        value=sp.TBytes,
    ).right_comb()
    Tree = sp.TRecord(
        root=sp.TBytes,
        root_edge=Edge,
        nodes=sp.TMap(sp.TBytes, Node),
        states=sp.TMap(sp.TBytes, sp.TBytes)
    ).right_comb()

    # Entry points
    Insert_argument = sp.TRecord(key=sp.TBytes, value=sp.TBytes).right_comb()
    Configure_argument = sp.TList(
        sp.TVariant(
            update_administrator=sp.TAddress,
            update_snapshot_duration=sp.TNat,
            update_max_state_size=sp.TNat
        ).right_comb()
    )

    # Views
    Get_proof_argument = sp.TRecord(
        owner=sp.TAddress,
        key=sp.TBytes
    ).right_comb()
    Get_proof_result = sp.TRecord(
        level=sp.TNat,
        merkle_root=sp.TBytes,
        key=sp.TBytes,
        value=sp.TBytes,
        proof=sp.TList(sp.TOr(sp.TBytes, sp.TBytes)),
    ).right_comb()
    Verify_proof_argument = sp.TRecord(
        proof=sp.TList(sp.TOr(sp.TBytes, sp.TBytes)), state=State
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
                    # This constant sets how many levels each snapshot has.
                    snapshot_duration=sp.TNat,
                    # This constant is used to limit the data length being inserted (in bytes).
                    max_state_size=sp.TNat,
                ),
                snapshot_start_level = sp.TNat,
                snapshot_counter     = sp.TNat,
                snapshot_level       = sp.TBigMap(sp.TNat, sp.TNat),
                merkle_tree          = Type.Tree
            ).right_comb()
        )

    @sp.entry_point()
    def snapshot(self):
        self.finalize_snapshot(True)

    @sp.entry_point(parameter_type=Type.Insert_argument)
    def insert(self, param):
        """
        Include new state into the merkle tree.
        """
        nat_of_bytes_lambda = sp.compute(sp.build_lambda(Nat.of_bytes))

        # Check and finalize snapshot
        self.finalize_snapshot(False)

        # Do not allow users to insert values bigger than max_state_size
        sp.verify(
            sp.len(param.value) <= self.data.config.max_state_size,
            Error.STATE_TOO_LARGE,
        )

        key_hash = sp.compute(Inlined.hash_key(ENCODE(sp.sender), param.key))
        key = sp.compute(
            sp.record(
                data=nat_of_bytes_lambda(key_hash),
                length=HASH_LENGTH,
            )
        )

        # Set new state
        state_hash = sp.compute(
            Inlined.hash_state(ENCODE(sp.sender), param.key, param.value)
        )
        self.data.merkle_tree.states[state_hash] = param.value

        with sp.if_(self.data.merkle_tree.root != NULL_HASH):
            # Skip on first insertion
            self.data.merkle_tree = self.insert_at_edge(
                sp.record(tree=self.data.merkle_tree, key=key, value=state_hash)
            )
        with sp.else_():
            edge = sp.compute(sp.record(key=key, node=state_hash))
            self.data.merkle_tree.root = Inlined.hash_edge(edge)
            self.data.merkle_tree.root_edge = edge

    @sp.entry_point(parameter_type=Type.Configure_argument)
    def configure(self, actions):
        # Only allowed addresses can call this entry point
        Inlined.failIfNotAdministrator(self)

        with sp.for_("action", actions) as action:
            with action.match_cases() as action:
                with action.match("update_administrator") as administrator:
                    self.data.config.administrator = administrator
                with action.match("update_snapshot_duration") as payload:
                    self.data.config.snapshot_duration = payload
                with action.match("update_max_state_size") as payload:
                    self.data.config.max_state_size = payload

    @sp.onchain_view()
    def get_proof(self, arg):
        """
        Returns the Merkle-proof for the given key.

        :argument:  sp.TRecord(
                        owner       = sp.TAddress,
                        key         = sp.TBytes,
                    )

        :returns:   sp.TRecord(
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
        nat_of_bytes_lambda = sp.compute(sp.build_lambda(Nat.of_bytes))

        key_hash = sp.compute(Inlined.hash_key(ENCODE(arg.owner), arg.key))
        key = sp.local(
            "key",
            sp.record(
                data=nat_of_bytes_lambda(key_hash),
                length=HASH_LENGTH,
            ),
        )

        tree = sp.local("tree", self.data.merkle_tree)
        root_edge = sp.local("root_edge", tree.value.root_edge)
        blinded_path = sp.local("blinded_path", [])

        continue_loop = sp.local("continue_loop", True)
        with sp.while_(continue_loop.value):
            (prefix, suffix) = sp.match_record(
                split_common_prefix_lambda((key.value, root_edge.value.key)),
                "prefix",
                "suffix",
            )
            sp.verify(prefix.length == root_edge.value.key.length, Error.PROOF_NOT_FOUND)

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
                                Inlined.hash_edge(
                                    tree.value.nodes[root_edge.value.node].children[1]
                                )
                            )
                        )
                    with sp.else_():
                        sp.result(
                            sp.left(
                                Inlined.hash_edge(
                                    tree.value.nodes[root_edge.value.node].children[0]
                                )
                            )
                        )

                blinded_path.value.push(hash.value)
                root_edge.value = tree.value.nodes[root_edge.value.node].children[head]
                key.value = tail

        with sp.set_result_type(Type.Get_proof_result):
            sp.result(
                sp.record(
                    level=sp.level,
                    key=arg.key,
                    value=tree.value.states[root_edge.value.node],
                    merkle_root=tree.value.root,
                    proof=blinded_path.value
                )
            )

    @sp.private_lambda(with_storage="read-write", with_operations=True, wrap_call=True)
    def finalize_snapshot(self, require):
        with sp.if_(self.data.snapshot_start_level == 0):
            # Start snapshot
            self.data.snapshot_start_level = sp.level
            self.data.merkle_tree = EMPTY_TREE

        with sp.if_(self.data.snapshot_start_level + self.data.config.snapshot_duration < sp.level):
            # Finalize snapshot
            self.data.snapshot_counter += 1
            self.data.snapshot_level[self.data.snapshot_counter] = sp.as_nat(sp.level-1)

            # Start snapshot
            self.data.snapshot_start_level = sp.level
            self.data.merkle_tree = EMPTY_TREE

            sp.emit(sp.record(snapshot= self.data.snapshot_counter, level = sp.level), with_type = True, tag = "SNAPSHOT_FINALIZED")
        with sp.else_():
            sp.verify(~require, Error.CANNOT_SNAPSHOT)


    @sp.onchain_view()
    def verify_proof(self, arg):
        """
        Validates a proof against a given state.
        """
        sp.set_type(arg, Type.Verify_proof_argument)

        state_hash = Inlined.hash_state(arg.state.owner, arg.state.key, arg.state.value)
        derived_hash = sp.local("derived_hash", state_hash)
        with sp.for_("el", arg.proof) as el:
            with el.match_cases() as cases:
                with cases.match("Left") as left:
                    derived_hash.value = HASH_FUNCTION(left + derived_hash.value)
                with cases.match("Right") as right:
                    derived_hash.value = HASH_FUNCTION(derived_hash.value + right)

        sp.verify((self.data.merkle_tree.root == derived_hash.value), Error.PROOF_INVALID)

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

                    new_node_hash = Inlined.replace_node(
                        tree, edge_node.open_some(), n.value
                    )

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
                                        node=Inlined.insert_node(
                                            tree, branch_node.value
                                        ),
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
            tree.value.root = Inlined.hash_edge(edge)
            tree.value.root_edge = edge

            sp.result(tree.value)
