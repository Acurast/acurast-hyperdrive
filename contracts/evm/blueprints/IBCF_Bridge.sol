// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

// --------------------------------------------------------------------------
// This contract implements a bridging protocol.
//
// It allows users to wrap/unwrap Ethereum assets on the Tezos blockchain.
// --------------------------------------------------------------------------

import "../libs/RLPReader.sol";
import {IBCF_Validator} from "../IBCF_Validator.sol";
import "./MintableERC20.sol";

library IBCF_Bridge_Error {
    string constant ALREADY_PROCESSED = "ALREADY_PROCESSED";
    string constant TEZOS_BRIDGE_ALREADY_SET = "TEZOS_BRIDGE_ALREADY_SET";
}

contract IBCF_Bridge {
    IBCF_Validator validator;
    MintableERC20 asset;
    bytes tezos_bridge_address;
    uint wrap_nonce;
    mapping(uint => bool) unwrap_nonce;
    // Proof slots
    mapping(uint => bytes) destination_registry;
    mapping(uint => uint) amount_registry;

    using RLPReader for RLPReader.RLPItem;
    using RLPReader for bytes;

    constructor(IBCF_Validator _validator, MintableERC20 _asset) {
        validator = _validator;
        asset = _asset;
    }

    event Wrap(bytes destination, uint amount, uint nonce);
    event Unwrap(address destination, uint amount, uint nonce);

    function set_tezos_bridge_address(bytes memory _tezos_bridge_address) public returns (bool) {
        require(tezos_bridge_address.length == 0, IBCF_Bridge_Error.TEZOS_BRIDGE_ALREADY_SET);
        tezos_bridge_address = _tezos_bridge_address;
        return true;
    }

    /**
     * @dev Wrap tokens on the Tezos blockchain.
     * @param destination The destination address.
     * @param amount The amount of tokens to wrap.
     */
    function wrap(bytes memory destination, uint amount) public {
        // Transfer assets
        asset.transferFrom(msg.sender, address(this), amount);

        // Update registry (The registry is used for proof generation)
        wrap_nonce += 1;
        destination_registry[wrap_nonce] = destination;
        amount_registry[wrap_nonce] = amount;

        emit Wrap(destination, amount, wrap_nonce);
    }

    /**
     * @dev Unwrap tokens from the Tezos blockchain.
     * @param snapshot The snapshot where the unwrap operation occured.
     * @param key The unwrap operation key in the merkle tree.
     * @param value The unwrap operation payload (destination and amount).
     * @param proof The operation proof.
     */
    function unwrap(
        uint snapshot,
        bytes memory key,
        bytes memory value,
        bytes32[2][] memory proof
    ) public {
        // Validate the proof
        validator.verify_proof(
            snapshot,
            tezos_bridge_address,
            key,
            value,
            proof
        );

        // Decode RLP bytes
        RLPReader.RLPItem[] memory args = value.toRlpItem().toList();
        address target_address = args[0].toAddress();
        uint amount = args[1].toUint();
        uint nonce = key.toRlpItem().toUint();

        // Verify if that wrap was not yet processed, fail otherwise
        require(!unwrap_nonce[nonce], IBCF_Bridge_Error.ALREADY_PROCESSED);
        // Register unwrap
        unwrap_nonce[nonce] = true;

        // Transfer tokens
        asset.transfer(target_address, amount);

        emit Unwrap(target_address, amount, nonce);
    }
}
