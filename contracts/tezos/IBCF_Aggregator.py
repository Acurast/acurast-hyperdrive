# --------------------------------------------------------------------------
# This implements a merkle tree to aggregate user provided states cheaply
# and generates proofs that can be validated in the Ethereum blockchain.
# ---------------------------------------------------------------------------

import smartpy as sp

from contracts.tezos.libs.patricia_trie import (
    chop_first_bit,
    split_common_prefix,
    remove_prefix,
    HASH_FUNCTION,
    HASH_LENGTH,
    NULL_HASH,
    EMPTY_TREE,
)
from contracts.tezos.libs.utils import Nat


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
        return sp.compute(HASH_FUNCTION(sp.concat([ENCODE(owner), key, value])))

    @staticmethod
    def hash_key(owner, key):
        return sp.compute(HASH_FUNCTION(sp.concat([ENCODE(owner), key])))

    @staticmethod
    def hash_edge(edge):
        # return HASH_FUNCTION(edge.node + sp.pack(edge.label))
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
    Edge = sp.TRecord(node=sp.TBytes, label=KeyMeta).right_comb()
    Node = sp.TRecord(children=sp.TMap(sp.TInt, Edge)).right_comb()
    Tree = sp.TRecord(
        root=sp.TBytes,
        root_edge=Edge,
        nodes=sp.TMap(sp.TBytes, Node),
        states=sp.TMap(sp.TBytes, sp.TBytes),
    ).right_comb()

    # Entry points
    Insert_argument = sp.TRecord(key=sp.TBytes, value=sp.TBytes).right_comb()
    Configure_argument = sp.TList(
        sp.TVariant(
            update_administrator=sp.TAddress,
            update_snapshot_duration=sp.TNat,
            update_max_state_size=sp.TNat,
        ).right_comb()
    )

    # Views
    Get_proof_argument = sp.TRecord(owner=sp.TAddress, key=sp.TBytes).right_comb()
    Get_proof_result = sp.TRecord(
        snapshot=sp.TNat,
        merkle_root=sp.TBytes,
        key=sp.TBytes,
        value=sp.TBytes,
        path=sp.TList(sp.TOr(sp.TBytes, sp.TBytes)),
    ).right_comb()
    Verify_proof_argument = sp.TRecord(
        path=sp.TList(sp.TOr(sp.TBytes, sp.TBytes)),
        state=sp.TRecord(
            owner=sp.TAddress,
            key=sp.TBytes,
            value=sp.TBytes,
        ).right_comb(),
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
                ).right_comb(),
                snapshot_start_level=sp.TNat,
                snapshot_counter=sp.TNat,
                snapshot_level=sp.TBigMap(sp.TNat, sp.TNat),
                merkle_tree=Type.Tree,
            ).right_comb()
        )
        self.init_entry_points_layout(("snapshot", ("insert", "configure")))

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

        key_hash = sp.compute(Inlined.hash_key(sp.sender, param.key))
        label = sp.compute(
            sp.record(
                data=nat_of_bytes_lambda(key_hash),
                length=HASH_LENGTH,
            )
        )

        # Set new state
        state_hash = sp.compute(Inlined.hash_state(sp.sender, param.key, param.value))
        self.data.merkle_tree.states[state_hash] = param.value

        with sp.if_(self.data.merkle_tree.root == NULL_HASH):
            # The tree is empty
            edge = sp.compute(sp.record(label=label, node=state_hash))
            self.data.merkle_tree.root = Inlined.hash_edge(edge)
            self.data.merkle_tree.root_edge = edge
        with sp.else_():
            tree, new_root_edge = sp.match_pair(
                self.insert_at_edge(
                    sp.record(
                        tree=self.data.merkle_tree,
                        edge=self.data.merkle_tree.root_edge,
                        key=label,
                        value=state_hash,
                    )
                )
            )

            self.data.merkle_tree = tree
            self.data.merkle_tree.root = Inlined.hash_edge(new_root_edge)
            self.data.merkle_tree.root_edge = new_root_edge

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
                        path       = sp.TList(sp.TOr(sp.TBytes, sp.TBytes))
                    )
        """
        sp.set_type(arg, Type.Get_proof_argument)

        chop_first_bit_lambda = sp.compute(sp.build_lambda(chop_first_bit))
        split_common_prefix_lambda = sp.compute(sp.build_lambda(split_common_prefix))
        nat_of_bytes_lambda = sp.compute(sp.build_lambda(Nat.of_bytes))

        key_hash = sp.compute(Inlined.hash_key(arg.owner, arg.key))
        label = sp.local(
            "label",
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
                split_common_prefix_lambda((label.value, root_edge.value.label)),
                "prefix",
                "suffix",
            )
            sp.verify(
                prefix.length == root_edge.value.label.length, Error.PROOF_NOT_FOUND
            )

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
                label.value = tail

        with sp.set_result_type(Type.Get_proof_result):
            sp.result(
                sp.record(
                    snapshot=self.data.snapshot_counter + 1,
                    key=arg.key,
                    value=tree.value.states[root_edge.value.node],
                    merkle_root=tree.value.root,
                    path=blinded_path.value,
                )
            )

    @sp.private_lambda(with_storage="read-write", with_operations=True, wrap_call=True)
    def finalize_snapshot(self, require):
        with sp.if_(self.data.snapshot_start_level == 0):
            # Start snapshot
            self.data.snapshot_start_level = sp.level
            self.data.merkle_tree = EMPTY_TREE

        with sp.if_(
            (
                self.data.snapshot_start_level + self.data.config.snapshot_duration
                < sp.level
            )
            & (self.data.merkle_tree.root != NULL_HASH)
        ):
            # Finalize snapshot
            self.data.snapshot_counter += 1

            # Snapshot previous block level
            snapshot_level = sp.compute(sp.as_nat(sp.level - 1))
            self.data.snapshot_level[self.data.snapshot_counter] = snapshot_level

            # Start new snapshot
            self.data.snapshot_start_level = sp.level
            self.data.merkle_tree = EMPTY_TREE

            sp.emit(
                sp.record(snapshot=self.data.snapshot_counter, level=snapshot_level),
                with_type=True,
                tag="SNAPSHOT_FINALIZED",
            )
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
        with sp.for_("el", arg.path) as el:
            with el.match_cases() as cases:
                with cases.match("Left") as left:
                    derived_hash.value = HASH_FUNCTION(left + derived_hash.value)
                with cases.match("Right") as right:
                    derived_hash.value = HASH_FUNCTION(derived_hash.value + right)

        sp.verify(
            (self.data.merkle_tree.root == derived_hash.value), Error.PROOF_INVALID
        )

    @sp.private_lambda(
        with_storage=None, with_operations=False, wrap_call=True, recursive=True
    )
    def insert_at_edge(self, arg, rec_call):
        (merkle_tree, edge, key, value) = sp.match_record(
            arg,
            "tree",
            "edge",
            "key",
            "value",
        )

        tree = sp.local("tree", merkle_tree)

        chop_first_bit_lambda = sp.compute(sp.build_lambda(chop_first_bit))
        remove_prefix_lambda = sp.compute(sp.build_lambda(remove_prefix))
        split_common_prefix_lambda = sp.compute(sp.build_lambda(split_common_prefix))

        # The key length must be bigger or equal to the edge lable length.
        sp.verify(key.length >= edge.label.length, "KEY_LENGTH_MISMATCH")

        (prefix, suffix) = sp.match_record(
            split_common_prefix_lambda((key, edge.label)),
            "prefix",
            "suffix",
        )

        result = sp.bind_block()
        with result:
            with sp.if_(suffix.length == 0):
                # Full match with the key, update operation
                sp.result((tree.value, value))
            with sp.else_():
                (head, tail) = sp.match_pair(chop_first_bit_lambda(suffix))

                with sp.if_(prefix.length >= edge.label.length):
                    # Partial match, just follow the path
                    sp.verify(suffix.length > 1, "BAD_KEY")

                    node = sp.local("node", tree.value.nodes[edge.node])

                    arg = sp.record(
                        tree=tree.value,
                        edge=node.value.children[head],
                        key=tail,
                        value=value,
                    )

                    (new_tree, new_edge) = sp.match_pair(rec_call(arg))
                    tree.value = new_tree

                    node.value.children[head] = new_edge
                    new_node_hash = Inlined.replace_node(tree, edge.node, node.value)

                    sp.result((tree.value, new_node_hash))
                with sp.else_():
                    # Mismatch, so let us create a new branch node.
                    branch_node = sp.compute(
                        sp.record(
                            children={
                                head: sp.record(node=value, label=tail),
                                (1 - head): sp.record(
                                    node=edge.node,
                                    label=remove_prefix_lambda(
                                        (edge.label, prefix.length + 1)
                                    ),
                                ),
                            }
                        )
                    )

                    new_node_hash = Inlined.insert_node(tree, branch_node)

                    sp.result((tree.value, new_node_hash))

        (new_tree, new_node_hash) = sp.match_pair(result.value)

        new_edge = sp.record(
            node=new_node_hash,
            label=prefix,
        )

        sp.result((new_tree, new_edge))
