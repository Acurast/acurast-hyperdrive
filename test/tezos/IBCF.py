import smartpy as sp

import contracts.tezos.state_aggregator
from contracts.tezos.state_aggregator import EMPTY_TREE, IBCF, ENCODE, Error
from contracts.tezos.utils.bytes import bytes_to_bits

contracts.tezos.state_aggregator.HASH_FUNCTION = sp.blake2b


@sp.add_test(name="IBCF")
def test():
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    claus = sp.test_account("claus")

    encoded_alice_address = ENCODE(alice.address)
    encoded_claus_address = ENCODE(claus.address)

    encoded_price_key = ENCODE("price")
    encoded_price_value_1 = ENCODE("1")
    encoded_price_value_2 = ENCODE("2")
    encoded_price_value_3 = ENCODE("3")

    BLOCK_LEVEL_1 = 1
    BLOCK_LEVEL_2 = 2

    scenario = sp.test_scenario()
    ibcf = IBCF()
    ibcf.update_initial_storage(
        sp.record(
            bytes_to_bits=bytes_to_bits,
            administrators=sp.set([admin.address]),
            merkle_history=sp.big_map(),
        )
    )

    scenario += ibcf

    # Add new administrator
    ibcf.update_administrators(sp.set([sp.variant("add", alice.address)])).run(
        sender=admin.address
    )
    scenario.verify(ibcf.data.administrators.contains(alice.address))
    # Remove administrator
    ibcf.update_administrators(sp.set([sp.variant("remove", alice.address)])).run(
        sender=admin.address
    )
    scenario.verify(~ibcf.data.administrators.contains(alice.address))

    # Try to remove an administrator without having permissions
    ibcf.update_administrators(sp.set([sp.variant("remove", alice.address)])).run(
        sender=bob.address, valid=False, exception=Error.NOT_ALLOWED
    )

    # Try to remove all administrators
    ibcf.update_administrators(sp.set([sp.variant("remove", admin.address)])).run(
        sender=admin.address,
        valid=False,
        exception=Error.AT_LEAST_ONE_ADMIN_IS_REQUIRED,
    )

    # Insert multiple states
    ibcf.insert(sp.record(key=encoded_price_key, value=encoded_price_value_1)).run(
        sender=alice.address, level=BLOCK_LEVEL_1
    )
    ibcf.insert(sp.record(key=encoded_price_key, value=encoded_price_value_2)).run(
        sender=bob.address, level=BLOCK_LEVEL_1
    )
    ibcf.insert(sp.record(key=encoded_price_key, value=encoded_price_value_2)).run(
        sender=claus.address, level=BLOCK_LEVEL_1
    )

    # Get proof of inclusion for key="price" and price="1"
    proof = ibcf.get_proof(
        sp.record(owner=alice.address, key=encoded_price_key, level=BLOCK_LEVEL_1)
    )

    # Verify proof for block 1 (Valid)
    ibcf.verify_proof(
        sp.record(
            level=BLOCK_LEVEL_1,
            proof=proof.proof,
            state=sp.record(
                owner=encoded_alice_address,
                key=encoded_price_key,
                value=encoded_price_value_1,
            ),
        )
    )

    # Verify proof for block 2 (Invalid)
    ex = sp.catch_exception(
        ibcf.verify_proof(
            sp.record(
                level=BLOCK_LEVEL_2,
                proof=proof.proof,
                state=sp.record(
                    owner=encoded_alice_address,
                    key=encoded_price_key,
                    value=encoded_price_value_1,
                ),
            )
        ),
        t=sp.TString,
    )
    scenario.verify(ex == sp.some(Error.PROOF_INVALID))

    # Insert multiple new states
    ibcf.insert(sp.record(key=encoded_price_key, value=encoded_price_value_2)).run(
        sender=alice.address, level=BLOCK_LEVEL_2
    )
    ibcf.insert(sp.record(key=encoded_price_key, value=encoded_price_value_1)).run(
        sender=bob.address, level=BLOCK_LEVEL_2
    )
    ibcf.insert(sp.record(key=encoded_price_key, value=encoded_price_value_3)).run(
        sender=claus.address, level=BLOCK_LEVEL_2
    )

    # Verify old proof on block 2 (Invalid)
    ex = sp.catch_exception(
        ibcf.verify_proof(
            sp.record(
                level=BLOCK_LEVEL_2,
                proof=proof.proof,
                state=sp.record(
                    owner=encoded_alice_address,
                    key=encoded_price_key,
                    value=encoded_price_value_1,
                ),
            )
        ),
        t=sp.TString,
    )
    scenario.verify(ex == sp.some(Error.PROOF_INVALID))

    # Get proof of inclusion for key="price" and price="1" on block 2
    proof = ibcf.get_proof(
        sp.record(owner=claus.address, key=encoded_price_key, level=BLOCK_LEVEL_2)
    )

    # Verify proof for block 2 (Valid)
    ibcf.verify_proof(
        sp.record(
            level=BLOCK_LEVEL_2,
            proof=proof.proof,
            state=sp.record(
                owner=encoded_claus_address,
                key=encoded_price_key,
                value=encoded_price_value_3,
            ),
        )
    )
