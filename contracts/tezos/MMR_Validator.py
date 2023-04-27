import smartpy as sp

from contracts.tezos.libs.utils import generate_var, Decorator


class Type:
    Leaf = sp.TRecord(
        # the leftmost index of a node
        k_index=sp.TNat,
        # The position in the tree
        mmr_pos=sp.TNat,
        # The hash of the position in the tree
        hash=sp.TBytes,
    ).right_comb()
    Node = sp.TRecord(
        # Distance of the node to the leftmost node
        k_index=sp.TNat,
        # A hash of the node itself
        hash=sp.TBytes,
    ).right_comb()

    # Entry points
    Configure_argument = sp.TList(
        sp.TVariant(
            update_governance_address=sp.TAddress,
            update_validators=sp.TSet(
                sp.TVariant(add=sp.TAddress, remove=sp.TAddress).right_comb()
            ),
            update_minimum_endorsements=sp.TNat,
            update_history_length=sp.TNat,
        ).right_comb()
    )
    Submit_root_argument = sp.TRecord(
        snapshot=sp.TNat,
        root=sp.TBytes,
    ).right_comb()

    # Views
    Verify_proof_argument = sp.TRecord(
        snapshot=sp.TNat,
        mmr_size=sp.TNat,
        leaves=sp.TList(Leaf),
        proof=sp.TList(sp.TBytes),
    ).right_comb()


class Iterator:
    def new(offset, stack):
        return sp.local(
            generate_var("iter"),
            sp.record(
                offset=offset,
                data=stack,
            ),
        )

    def type(t):
        return sp.TRecord(
            offset=sp.TInt,
            data=sp.Map(tkey=sp.TNat, tvalue=t),
        ).right_comb()

    def push(iterator, data):
        iterator.value.data[iterator.value.offset] = data
        iterator.value.offset += 1

    def next(iterator):
        value = sp.compute(iterator.value.data[iterator.value.offset])

        iterator.value.offset += 1

        return value

    def previous(iterator):
        value = sp.compute(iterator.value.data[iterator.value.offset])

        iterator.value.offset -= 1

        return value


@Decorator.generate_lambda()
def merge_maps(arg):
    (l1, l2) = sp.match_pair(arg)

    result = sp.local(generate_var("result"), l1)
    l2_index = sp.local(generate_var("l2_index"), 0)
    index = sp.local(generate_var("index"), sp.len(result.value))
    length = sp.compute(sp.len(l1) + sp.len(l2))
    with sp.while_(index.value < length):
        result.value[index.value] = l2[l2_index.value]
        l2_index.value += 1
        index.value += 1

    sp.result(result.value)


@Decorator.generate_lambda()
def merge(arg):
    (left, right) = sp.match_pair(arg)
    sorted = sp.local(
        generate_var("sorted"), sp.map(tkey=sp.TIntOrNat, tvalue=Type.Node)
    )
    sorted_index = sp.local(generate_var("sorted_index"), 0)

    left_i = sp.local(generate_var("left_i"), 0)
    right_i = sp.local(generate_var("right_i"), 0)
    left_size = sp.local(generate_var("left_size"), sp.len(left))
    right_size = sp.local(generate_var("right_size"), sp.len(right))

    with sp.while_(
        (left_size.value > left_i.value) & (right_size.value > right_i.value)
    ):
        left_el = left[left_i.value]
        right_el = right[right_i.value]
        with sp.if_(left_el.k_index < right_el.k_index):
            sorted.value[sorted_index.value] = left_el
            left_i.value += 1
        with sp.else_():
            sorted.value[sorted_index.value] = right_el
            right_i.value += 1

        sorted_index.value += 1

    # push remaining values
    with sp.while_(left_size.value > left_i.value):
        sorted.value[sorted_index.value] = left[left_i.value]
        left_i.value += 1
        sorted_index.value += 1
    with sp.while_(right_size.value > right_i.value):
        sorted.value[sorted_index.value] = right[right_i.value]
        right_i.value += 1
        sorted_index.value += 1

    sp.result(sorted.value)


@Decorator.generate_lambda(with_operations=False, recursive=True)
def merge_sort(indexed_list, merge_sort):
    length = sp.compute(sp.len(indexed_list))
    with sp.if_(length > 1):
        middle = sp.local(generate_var("middle"), sp.to_int(length / 2))

        left_l = sp.local(generate_var("left_l"), sp.map())
        left_i = sp.local(generate_var("left_i"), 0)
        right_l = sp.local(generate_var("right_l"), sp.map())
        right_i = sp.local(generate_var("right_i"), 0)
        index = sp.local(generate_var("index"), 0)
        with sp.while_(index.value < length):
            element = sp.compute(indexed_list[index.value])
            with sp.if_(middle.value > 0):
                left_l.value[left_i.value] = element
                left_i.value += 1
            with sp.else_():
                right_l.value[right_i.value] = element
                right_i.value += 1

            index.value += 1
            middle.value -= 1

        left = sp.compute(merge_sort(left_l.value))
        right = sp.compute(merge_sort(right_l.value))

        sp.result(merge((left, right)))
    with sp.else_():
        sp.result(indexed_list)


class MultiProof:
    @Decorator.generate_lambda()
    def calculate_root(arg):
        """
        Calculate the hash of the root node

        @param proof A list of the merkle nodes along with their k-indices that are needed to re-calculate root node
        @param leaves A list of the along with their k-indices to prove
        @return Hash of root node
        """

        # Add lambdas to the stack
        merge_sort_f = sp.compute(merge_sort)
        merge_maps_f = sp.compute(merge_maps)

        (proof, leaves) = sp.match_pair(arg)

        # Holds the output from hashing a previous layer
        next_layer = sp.local(
            generate_var("next_layer"), sp.map(tkey=sp.TIntOrNat, tvalue=Type.Node)
        )

        # Merge leaves
        dyn_proof = sp.local(generate_var("dyn_proof"), proof)
        dyn_proof.value[0] = merge_sort_f(merge_maps_f((leaves, proof[0])))

        proof_length = sp.compute(sp.to_int(sp.len(dyn_proof.value)))
        height = sp.local(generate_var("height"), sp.int(0))
        with sp.while_(height.value < proof_length):
            current_layer = sp.local(
                generate_var("current_layer"),
                sp.map(tkey=sp.TIntOrNat, tvalue=Type.Node),
            )
            height_proof = sp.compute(dyn_proof.value[height.value])
            with sp.if_(sp.len(next_layer.value) == 0):
                current_layer.value = height_proof
            with sp.else_():
                current_layer.value = merge_sort_f(
                    merge_maps_f((height_proof, next_layer.value))
                )

            next_layer.value = sp.map()
            next_layer_index = sp.local(generate_var("next_layer_index"), 0)

            current_layer_length = sp.compute(sp.len(current_layer.value))
            index = sp.local(generate_var("index"), 0)
            with sp.while_(index.value < current_layer_length):
                node = sp.local(generate_var("node"), current_layer.value[index.value])
                node.value.k_index = node.value.k_index / 2
                with sp.if_((index.value + 1) >= current_layer_length):
                    next_layer.value[next_layer_index.value] = node.value
                with sp.else_():
                    next_node = current_layer.value[index.value + 1].hash
                    node.value.hash = sp.keccak(node.value.hash + next_node)
                    next_layer.value[next_layer_index.value] = node.value
                    next_layer_index.value += 1

                index.value += 2

            height.value += 1

        # Ensure the root node has been reached
        sp.verify(sp.len(next_layer.value) == 1, "NOT_ROOT_NODE")

        sp.result(next_layer.value[0].hash)


class MMR:
    def leaf_count_to_mmr_size(leaf_count):
        return sp.as_nat((2 * leaf_count) - MMR.count_ones(leaf_count))

    def calculate_root(proof, leaves, mmr_size):
        """
        Calculate merkle root

        @param proof A list of the merkle nodes that are needed to re-calculate root node
        @param leaves a list of mmr leaves to prove
        @param mmr_size the size of the merkle tree
        @return Hash of root node
        """
        peaks = sp.compute(
            sp.build_lambda(lambda x: sp.result(MMR.get_peaks(x)))(mmr_size)
        )
        peak_roots = Iterator.new(0, sp.map())
        proof_iter = Iterator.new(0, proof)

        dyn_leaves = sp.local(generate_var("dyn_leaves"), leaves)

        in_loop = sp.local(generate_var("in_loop"), True)
        with sp.for_("peak", peaks) as peak:
            with sp.if_(in_loop.value):
                peak_leaves = sp.local(generate_var("peak_leaves"), sp.map())

                with sp.if_(sp.len(dyn_leaves.value) > 0):
                    result = MMR.leaves_for_peak(dyn_leaves.value, peak)
                    peak_leaves.value = sp.fst(result)
                    dyn_leaves.value = sp.snd(result)

                peak_leaves_length = sp.compute(sp.len(peak_leaves.value))
                with sp.if_(peak_leaves_length == 0):
                    with sp.if_(
                        sp.to_int(sp.len(proof_iter.value.data))
                        == proof_iter.value.offset
                    ):
                        in_loop.value = False
                    with sp.else_():
                        Iterator.push(peak_roots, Iterator.next(proof_iter))
                with sp.else_():
                    with sp.if_(
                        (peak_leaves_length == 1)
                        & (peak_leaves.value[0].mmr_pos == peak)
                    ):
                        Iterator.push(peak_roots, peak_leaves.value[0].hash)
                    with sp.else_():
                        peak_root = MMR.calculate_peak_root(
                            peak_leaves.value, proof_iter, peak
                        )
                        Iterator.push(peak_roots, peak_root)

        peak_roots.value.offset -= 1

        with sp.while_(peak_roots.value.offset != 0):
            right = sp.compute(Iterator.previous(peak_roots))
            left = sp.compute(Iterator.previous(peak_roots))

            peak_roots.value.offset += 1

            peak_roots.value.data[peak_roots.value.offset] = sp.keccak(right + left)

        return peak_roots.value.data[0]

    def calculate_peak_root(peak_leaves, proof_iter, peak):
        """
        Calculate root hash of a sub peak of the merkle mountain

        @param peak_leaves : A list of nodes to provide proof for
        @param proof_iter  : A list of node hashes to traverse to compute the peak root hash
        @param peak        : The index of the peak node
        @return A tuple containing the peak root hash, and the peak root position in the merkle
        """
        res = sp.compute(MMR.mmr_leaf_to_node(peak_leaves))
        leaves = sp.local(generate_var("leaves"), sp.fst(res))
        current_layer = sp.local(generate_var("current_layer"), sp.snd(res))

        height = sp.compute(MMR.pos_to_height(peak))
        layers = sp.local(
            generate_var("layers"),
            sp.map(tkey=sp.TIntOrNat, tvalue=sp.TMap(sp.TIntOrNat, Type.Node)),
        )

        i = sp.local(generate_var("i"), 0)
        in_loop = sp.local(generate_var("in_loop"), True)
        with sp.while_(in_loop.value & (i.value < height)):
            layers.value[i.value] = sp.map()

            siblings = sp.compute(MMR.sibling_indices(current_layer.value))
            diff = sp.compute(MMR.difference(siblings, current_layer.value))

            diff_length = sp.compute(sp.len(diff))
            with sp.if_(diff_length == 0):
                in_loop.value = False
            with sp.else_():
                j = sp.local(generate_var("j"), 0)
                with sp.for_("el", diff.elements()) as el:
                    layers.value[i.value][j.value] = sp.record(
                        k_index=el, hash=Iterator.next(proof_iter)
                    )
                    j.value += 1

                current_layer.value = MMR.parent_indices(siblings)

            i.value += 1

        return MultiProof.calculate_root((layers.value, leaves.value))

    def difference(left, right):
        diff = sp.local(generate_var("diff"), sp.map())
        diff_count = sp.local(generate_var("diff_count"), 0)

        left_length = sp.compute(sp.len(left))
        left_i = sp.local(generate_var("left_i"), 0)
        right_length = sp.compute(sp.len(right))
        with sp.while_(left_i.value < left_length):
            left_element = sp.compute(left[left_i.value])
            found = sp.local(generate_var("found"), False)

            right_i = sp.local(generate_var("right_i"), 0)
            with sp.while_(right_i.value < right_length):
                found.value |= left_element == right[right_i.value]
                right_i.value += 1

            with sp.if_(~found.value):
                diff.value[diff_count.value] = left_element
                diff_count.value += 1

            left_i.value += 1

        out = sp.local(generate_var("out"), sp.set())
        out_index = sp.local(generate_var("out_index"), 0)
        with sp.while_(out_index.value < diff_count.value):
            out.value.add(diff.value[out_index.value])
            out_index.value += 1

        return out.value

    def sibling_indices(indices):
        """
        Calculates the index of each sibling index of the proof nodes

        @param indices : A list of proof nodes indices
        @return a list of sibling indices
        """
        siblings = sp.local(generate_var("siblings"), sp.map())

        length = sp.compute(sp.len(indices))
        i = sp.local("i", 0)
        with sp.while_(i.value < length):
            index = sp.compute(indices[i.value])
            with sp.if_(index % 2 == 0):
                siblings.value[i.value] = index + 1
            with sp.else_():
                siblings.value[i.value] = sp.as_nat(index - 1)

            i.value += 1

        return siblings.value

    def parent_indices(indices):
        """
        Compute Parent Indices

        @param indices : A list of indices of proof nodes in a merkle mountain
        @return a list of parent indices for each index provided
        """
        parents = sp.local(generate_var("parents"), sp.map())

        length = sp.compute(sp.len(indices))
        i = sp.local("i", 0)
        with sp.while_(i.value < length):
            index = sp.compute(indices[i.value])
            parents.value[i.value] = index / 2
            i.value += 1

        return parents.value

    def mmr_leaf_to_node(leaves):
        """
        Convert Merkle mountain leaf to a Merkle node

        @param leaves : A list of merkle mountain range leaves
        @return a tuple with the list of merkle nodes and the list of nodes at 0 and 1 respectively
        """
        nodes = sp.local(generate_var("parents"), sp.map())
        indices = sp.local(generate_var("indices"), sp.map())

        index = sp.local(generate_var("index"), 0)
        length = sp.compute(sp.len(leaves))
        with sp.while_(index.value < length):
            leaf = sp.compute(leaves[index.value])
            nodes.value[index.value] = sp.record(k_index=leaf.k_index, hash=leaf.hash)
            indices.value[index.value] = leaf.k_index
            index.value += 1

        return (nodes.value, indices.value)

    def leaves_for_peak(leaves, peak):
        """
        Get the mountain peak leaves, splits the leaves into either side of the peak [left & right]

        @param leaves a list of mountain merkle leaves, for a subtree
        @param peak the peak index of the root of the subtree

        @return A tuple that represents the left and right sides of the peak respectively
        """

        left = sp.local(generate_var("left"), sp.map())
        left_i = sp.local(generate_var("left_i"), 0)
        right = sp.local(generate_var("right"), sp.map())
        right_i = sp.local(generate_var("right_i"), 0)
        length = sp.local(generate_var("length"), 0)
        add_right = sp.local(generate_var("add_right"), False)
        with sp.for_("leaf", leaves.values()) as leaf:
            with sp.if_(add_right.value | (peak < leaf.mmr_pos)):
                right.value[right_i.value] = leaf
                right_i.value += 1
                add_right.value = True
            with sp.else_():
                left.value[left_i.value] = leaf
                left_i.value += 1

        return (left.value, right.value)

    def get_peaks(mmr_size):
        """
        Merkle mountain peaks computer

        @param mmr_size : The size of the merkle mountain range, or the height of the tree
        @return a list of the peak positions
        """
        (height, pos) = sp.match_pair(MMR.left_peak_height_pos(mmr_size))
        positions = sp.local(generate_var("positions"), sp.list([pos]))
        dyn_height = sp.local(generate_var("dyn_height"), height)
        dyn_pos = sp.local(generate_var("dyn_pos"), pos)

        in_loop = sp.local(generate_var("in_loop"), True)
        with sp.while_(in_loop.value & (dyn_height.value > 0)):
            (_height, _pos) = sp.match_pair(
                MMR.get_right_peak(dyn_height.value, dyn_pos.value, mmr_size)
            )
            with sp.if_((_height == 0) & (_pos == 0)):
                in_loop.value = False
            with sp.else_():
                positions.value.push(_pos)
                dyn_height = _height
                dyn_pos.value = _pos

        return positions.value.rev()

    def get_right_peak(height, pos, mmr_size):
        mmr_size_ = sp.compute(sp.as_nat(mmr_size - 1))
        dyn_pos = sp.local(generate_var("dyn_pos"), pos + MMR.sibling_offset(height))
        dyn_height = sp.local(generate_var("dyn_height"), height)
        result = sp.local(generate_var("result"), sp.none)
        with sp.while_(result.value.is_none() & (dyn_pos.value > mmr_size_)):
            with sp.if_(dyn_height.value == 0):
                result.value = sp.some((0, 0))
            with sp.else_():
                dyn_height.value = sp.as_nat(dyn_height.value - 1)
                dyn_pos.value = sp.as_nat(
                    dyn_pos.value - MMR.parent_offset(dyn_height.value)
                )

        with sp.if_(result.value.is_none()):
            result.value = sp.some((dyn_height.value, dyn_pos.value))

        return result.value.open_some()

    def get_peak_pos_by_height(height):
        return sp.as_nat((1 << (height + 1)) - 2, "NEGATIVE_RESULT")

    def left_peak_height_pos(mmrSize):
        # Lambdas
        getPeakPosByHeight = sp.compute(
            sp.build_lambda(lambda h: sp.result(MMR.get_peak_pos_by_height(h)))
        )

        height = sp.local(generate_var("height"), 1)
        pos = sp.local(generate_var("pos"), getPeakPosByHeight(height.value))
        prevPos = sp.local(generate_var("prevPos"), 0)
        with sp.while_(pos.value < mmrSize):
            prevPos.value = pos.value
            height.value += 1
            pos.value = getPeakPosByHeight(height.value)

        return sp.pair(sp.as_nat(height.value - 1), prevPos.value)

    def pos_to_height(pos):
        dyn_pos = sp.local(generate_var("pos"), pos + 1)

        in_loop = sp.local("in_loop", MMR.all_ones(dyn_pos.value))
        with sp.while_(~in_loop.value):
            dyn_pos.value = MMR.jump_left(dyn_pos.value)
            in_loop.value = MMR.all_ones(dyn_pos.value)

        return 64 - MMR.count_leading_zeros(dyn_pos.value) - 1

    def parent_offset(height):
        return 2 << height

    def sibling_offset(height):
        return sp.as_nat(MMR.parent_offset(height) - 1)

    def count_ones(num):
        counter = sp.local(generate_var("counter"), 0)
        value = sp.local(generate_var("value"), num)

        with sp.while_(value.value > 0):
            value.value &= abs(value.value - 1)
            counter.value += 1

        return counter.value

    def count_zeros(num):
        return sp.as_nat(64 - MMR.count_ones(num), "NEGATIVE_RESULT")

    def count_leading_zeros(num):
        size = 64
        msb = 1 << 63
        counter = sp.local(generate_var("counter"), sp.nat(0))

        i = sp.local(generate_var("i"), 0)
        break_loop = sp.local(generate_var("break_loop"), False)
        with sp.while_(~break_loop.value & (i.value < size)):

            with sp.if_(((num << i.value) & msb) != 0):
                break_loop.value = True
            with sp.else_():
                counter.value += 1

            i.value += 1

        return counter.value

    def all_ones(num):
        zeros = sp.compute(MMR.count_zeros(num))
        leading_zeros = sp.compute(MMR.count_leading_zeros(num))
        return (num != 0) & (zeros == leading_zeros)

    def jump_left(num):
        len = sp.as_nat(64 - MMR.count_leading_zeros(num), "NEGATIVE_RESULT")
        msb = 1 << sp.as_nat(len - 1, "NEGATIVE_RESULT")
        return sp.as_nat(sp.to_int(num) - (msb - 1), "NEGATIVE_RESULT")

    def leaf_index_to_pos(index):
        # mmr_size - H - 1, H is the height(intervals) of last peak
        mmr_size = MMR.leaf_index_to_mmr_size(index)
        height = MMR.trailing_zeros(index + 1)
        return sp.as_nat((mmr_size - height) - sp.int(1), "NEGATIVE_RESULT")

    # count leading zeros: https://stackoverflow.com/a/45222481/6394734
    def trailing_zeros(x):
        result = sp.local(generate_var("result"), 0)

        with sp.if_(x == 0):
            result.value = 32
        with sp.else_():
            n = sp.local(generate_var("n"), 1)
            y = sp.local(generate_var("y"), x)

            with sp.if_((y.value & 0x0000FFFF) == 0):
                n.value += 16
                y.value = y.value >> 16

            with sp.if_((y.value & 0x000000FF) == 0):
                n.value += 8
                y.value = y.value >> 8

            with sp.if_((y.value & 0x0000000F) == 0):
                n.value += 4
                y.value = y.value >> 4

            with sp.if_((y.value & 0x00000003) == 0):
                n.value += 2
                y.value = y.value >> 2

            result.value = sp.as_nat(n.value - (y.value & 1), "NEGATIVE_RESULT")

        return result.value

    def leaf_index_to_mmr_size(index):
        # leaf index start with 0
        leaves_count = sp.compute(index + 1)

        # the peak count(k) is actually the count of 1 in leaves count's binary representation
        peak_count = MMR.count_ones(leaves_count)

        return sp.as_nat((2 * leaves_count) - peak_count, "NEGATIVE_RESULT")


class Error:
    NOT_GOVERNANCE = "NOT_GOVERNANCE_ADDRESS"
    NOT_VALIDATOR = "NOT_VALIDATOR"
    INVALID_SNAPSHOT = "INVALID_SNAPSHOT"
    UNKNOWN_SNAPSHOT = "UNKNOWN_SNAPSHOT"
    INVALID_PROOF = "INVALID_PROOF"


class Inlined:
    @staticmethod
    def failIfNotGovernance(self):
        """
        This method when used, ensures that only the governance address is allowed to call a given entrypoint
        """
        sp.verify(
            self.data.config.governance_address == sp.sender, Error.NOT_GOVERNANCE
        )

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


class MMR_Validator(sp.Contract):
    def __init__(self):
        self.init_type(
            sp.TRecord(
                config=sp.TRecord(
                    # Multi-sig address allowed to manage the contract
                    governance_address=sp.TAddress,
                    # Minimum expected endorsements for a given state root to be considered valid
                    minimum_endorsements=sp.TNat,
                    # Validators
                    validators=sp.TSet(sp.TAddress),
                ),
                current_snapshot=sp.TNat,
                root=sp.TBigMap(sp.TNat, sp.TBytes),
                snapshot_submissions=sp.TMap(sp.TAddress, sp.TBytes),
            )
        )

    @sp.entry_point(parameter_type=Type.Submit_root_argument)
    def submit_root(self, arg):
        (snapshot, root) = sp.match_record(
            arg,
            "snapshot",
            "root",
        )

        # Check if sender is a validator
        Inlined.failIfNotValidator(self)

        # Make sure the snapshots are submitted sequencially
        sp.verify(self.data.current_snapshot == snapshot, Error.INVALID_SNAPSHOT)

        # Store the root per validator
        self.data.snapshot_submissions[sp.sender] = root

        # Finalize snapshot if consensus has been reached
        can_finalize_snapshot = sp.compute(
            sp.build_lambda(Lambdas.validate_block_state_root)(
                sp.record(
                    state_roots=self.data.snapshot_submissions,
                    minimum_endorsements=self.data.config.minimum_endorsements,
                )
            ).is_some()
        )

        with sp.if_(can_finalize_snapshot):
            self.data.root[self.data.current_snapshot] = root
            self.data.current_snapshot += 1
            self.data.snapshot_submissions = sp.map()

    @sp.entry_point(
        parameter_type=sp.TRecord(from_=sp.TNat, to=sp.TNat).layout(
            ("from_ as from", "to")
        )
    )
    def remove_old_roots(self, arg):
        # Only the governance address can call this entry point
        Inlined.failIfNotGovernance(self)

        snapshot = sp.local("snapshot", arg.from_)
        with sp.while_(snapshot.value < arg.to):
            del self.data.root[snapshot.value]
            snapshot.value += 1

    @sp.entry_point(parameter_type=Type.Configure_argument)
    def configure(self, actions):

        # Only allowed addresses can call this entry point
        Inlined.failIfNotGovernance(self)

        with sp.for_("action", actions) as action:
            with action.match_cases() as action:
                with action.match("update_validators") as payload:
                    with sp.for_("el", payload.elements()) as el:
                        with el.match_cases() as cases:
                            with cases.match("add") as add:
                                self.data.config.validators.add(add)
                            with cases.match("remove") as remove:
                                self.data.config.validators.remove(remove)
                with action.match("update_governance_address") as governance_address:
                    self.data.config.governance_address = governance_address
                with cases.match("update_minimum_endorsements") as payload:
                    self.data.config.minimum_endorsements = payload

    @sp.onchain_view()
    def verify_proof(self, arg):
        """
        Verify that MMR proof is valid against a given snapshot
        @param snapshot : The snapshot where the proof was generated
        @param proof : A proof of the authenticity of the `leaves`
        @param leaves : A list of states (leaves)
        @return `True` if the calculated root matches the provided snapshot root hash, `False` otherwise
        """
        (leaves, mmr_size, proof, snapshot,) = sp.match_record(
            sp.set_type_expr(
                arg,
                Type.Verify_proof_argument,
            ),
            "leaves",
            "mmr_size",
            "proof",
            "snapshot",
        )

        index = sp.local("index", 0)
        indexed_leaves = sp.local("indexed_leaves", sp.map())
        with sp.for_("leaf", arg.leaves) as leaf:
            indexed_leaves.value[index.value] = leaf
            index.value += 1

        index.value = 0
        indexed_proof = sp.local("indexed_proof", sp.map())
        with sp.for_("node", arg.proof) as node:
            indexed_proof.value[index.value] = node
            index.value += 1

        # Get snapshot root
        root = sp.compute(
            self.data.root.get(arg.snapshot, message=Error.UNKNOWN_SNAPSHOT)
        )
        with sp.for_("proof_node", proof) as proof_node:
            sp.verify(proof_node != root, Error.INVALID_PROOF)

        # Compute root from proof
        computed_hash = MMR.calculate_root(
            indexed_proof.value, indexed_leaves.value, arg.mmr_size
        )

        # Validate proof result
        sp.result(root == computed_hash)

    # @sp.entry_point(
    #     parameter_type = sp.TRecord(
    #         root = sp.TBytes,
    #         proof = sp.TList(sp.TVariant(message = sp.TBytes, merge_op = sp.TBool, node = sp.TBytes))
    #     )
    # )
    # def receive_message(self, arg):
    #     progress_stack = sp.local(generate_var("progress_stack"), sp.map(tkey=sp.TIntOrNat, tvalue = sp.TBytes))
    #     messages = sp.local(generate_var("messages"), sp.map())

    #     with sp.for_("element", arg.proof) as el:
    #         with el.match_cases() as value:
    #             with value.match("message") as message:
    #                 messages.value[sp.len(messages.value)] = message
    #                 progress_stack.value[sp.len(progress_stack.value)] = message
    #             with value.match("node") as node:
    #                 progress_stack.value[sp.len(progress_stack.value)] = node
    #             with value.match("merge_op") as reversed:
    #                 stack_size = sp.compute(sp.len(progress_stack.value))
    #                 sp.verify(stack_size >= 2, "EXPECTED_TWO_NODES")
    #                 el1_index = abs(stack_size-2) # ABS is cheaper than IS_NAT (We already know that there are at least 2 nodes)
    #                 el2_index = abs(stack_size-1) # ABS is cheaper than IS_NAT (We already know that there are at least 2 nodes)

    #                 el1_bytes = sp.compute(progress_stack.value[el1_index])
    #                 el2_bytes = sp.compute(progress_stack.value[el2_index])

    #                 del progress_stack.value[el2_index]

    #                 with sp.if_(reversed):
    #                     progress_stack.value[el1_index] = sp.keccak(el2_bytes + el1_bytes)
    #                 with sp.else_():
    #                     progress_stack.value[el1_index] = sp.keccak(el1_bytes + el2_bytes)

    #     sp.verify(arg.root == progress_stack.value[0], ("PROOF_INVALID", progress_stack.value))


# class MMR_Validator_Proxy(sp.Contract):
#     class Error:
#         INVALID_VIEW = "INVALID_VIEW"

#     def __init__(self):
#         self.init_type(
#             sp.TRecord(
#                 validator_address=sp.TAddress,
#             )
#         )

#     @sp.onchain_view()
#     def verify_proof(self, arg):
#         sp.set_type(arg, Type.Verify_proof_argument)
#         is_valid = sp.view("verify_proof", self.data.validator_address, arg, t = sp.TBool).open_some(MMR_Validator_Proxy.Error.INVALID_VIEW)
#         sp.result(is_valid)
