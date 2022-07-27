import smartpy as sp

import contracts.tezos.IBCF_Aggregator
from contracts.tezos.IBCF_Aggregator import IBCF_Aggregator, ENCODE, Error
from contracts.tezos.utils.bytes import bytes_to_bits

contracts.tezos.IBCF_Aggregator.HASH_FUNCTION = sp.blake2b


def update_signers(payload):
    return sp.variant("update_signers", payload)


def update_administrator(payload):
    return sp.variant("update_administrator", payload)


def update_history_ttl(payload):
    return sp.variant("update_history_ttl", payload)


def update_max_state_size(payload):
    return sp.variant("update_max_state_size", payload)


def update_max_states(payload):
    return sp.variant("update_max_states", payload)


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
    ibcf = IBCF_Aggregator()
    ibcf.update_initial_storage(
        sp.record(
            config=sp.record(
                administrator=admin.address,
                signers=sp.set(),
                history_ttl=5,
                max_state_size=32,
                max_states=1000,
            ),
            bytes_to_bits=bytes_to_bits,
            merkle_history=sp.big_map(),
            merkle_history_indexes=[],
        )
    )

    scenario += ibcf

    # Update administrator
    ibcf.configure(update_administrator(alice.address)).run(sender=admin.address)
    scenario.verify(ibcf.data.config.administrator == alice.address)
    ibcf.configure(update_administrator(admin.address)).run(sender=alice.address)
    scenario.verify(ibcf.data.config.administrator == admin.address)

    # Add signers
    ibcf.configure(
        update_signers(
            sp.set(
                [
                    sp.variant("add", alice.address),
                    sp.variant("add", bob.address),
                    sp.variant("add", claus.address),
                ]
            )
        )
    ).run(sender=admin.address)
    scenario.verify(ibcf.data.config.signers.contains(claus.address))
    # Remove signer
    ibcf.configure(update_signers(sp.set([sp.variant("remove", claus.address)]))).run(
        sender=admin.address
    )
    scenario.verify(~ibcf.data.config.signers.contains(claus.address))

    # Try to remove a signer without having permissions
    ibcf.configure(update_signers(sp.set([sp.variant("remove", alice.address)]))).run(
        sender=bob.address, valid=False, exception=Error.NOT_ALLOWED
    )

    # Update history_ttl
    ibcf.configure(update_history_ttl(10)).run(
        sender=admin.address,
    )
    scenario.verify(ibcf.data.config.history_ttl == 10)

    # Update max_state_size
    ibcf.configure(update_max_state_size(16)).run(
        sender=admin.address,
    )
    scenario.verify(ibcf.data.config.max_state_size == 16)
    ibcf.configure(update_max_state_size(32)).run(
        sender=admin.address,
    )

    # Update max_states
    ibcf.configure(update_max_states(15)).run(
        sender=admin.address,
    )
    scenario.verify(ibcf.data.config.max_states == 15)

    # Do not allow states bigger than 32 bytes
    ibcf.insert(
        sp.record(key=encoded_price_key, value=sp.bytes("0x" + ("00" * 33)))
    ).run(
        sender=alice.address,
        level=BLOCK_LEVEL_1,
        valid=False,
        exception=Error.STATE_TOO_LARGE,
    )
    # states with 32 bytes or less are allowed
    ibcf.insert(
        sp.record(key=encoded_price_key, value=sp.bytes("0x" + ("00" * 32)))
    ).run(sender=alice.address, level=BLOCK_LEVEL_1)

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

    # Submit a signature for a given level
    proof = ibcf.submit_signature(
        sp.record(
            level=BLOCK_LEVEL_1,
            signature=sp.record(
                r=sp.bytes("0x01"),
                s=sp.bytes("0x02"),
            ),
        )
    ).run(sender=alice.address)
    # Try to submit a signature for a given level without being a signer
    proof = ibcf.submit_signature(
        sp.record(
            level=BLOCK_LEVEL_1,
            signature=sp.record(
                r=sp.bytes("0x01"),
                s=sp.bytes("0x02"),
            ),
        )
    ).run(sender=claus.address, valid=False, exception=Error.NOT_SIGNER)

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
