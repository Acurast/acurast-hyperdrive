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
    string constant INVALID_NONCE = "INVALID_NONCE";
    string constant TEZOS_BRIDGE_ALREADY_SET = "TEZOS_BRIDGE_ALREADY_SET";
}

contract IBCF_Bridge {
    IBCF_Validator validator;
    MintableERC20 asset;
    bytes tezos_bridge_address;
    mapping(bytes => uint) wrap_nonce; // Tezos address => nonce
    mapping(address => uint) unwrap_nonce; // Eth address => nonce
    mapping(bytes => uint) registry; // (Tezos address + nonce) RLP encoded => amount RLP encoded

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
     * @param target_address The destination address.
     * @param amount The amount of tokens to wrap.
     */
    function wrap(bytes memory target_address, uint amount) public {
        // Transfer assets
        asset.transferFrom(msg.sender, address(this), amount);
        // Update registry (The registry is used for proof generation)
        uint nonce = wrap_nonce[target_address] + 1;
        wrap_nonce[target_address] = nonce;
        registry[abi.encodePacked(target_address, nonce)] = amount;

        emit Wrap(target_address, amount, nonce);
    }

    /**
     * @dev Unwrap tokens from the Tezos blockchain.
     * @param block_level The block level where the unwrap operation occured.
     * @param merkle_root The block merkle root.
     * @param key The unwrap operation key in the merkle tree.
     * @param value The unwrap operation payload (destination and amount).
     * @param proof The operation proof.
     * @param _signers A list of bridge validators. (Gas optimization)
     * @param signatures A list of signatures for each validator (uses the same order as _signers)
     */
    function unwrap(
        uint block_level,
        bytes32 merkle_root,
        bytes memory key,
        bytes memory value,
        bytes32[2][] memory proof,
        address[] memory _signers,
        uint[2][] memory signatures
    ) public {
        // Validate the proof
        validator.verify_proof(
            block_level,
            merkle_root,
            tezos_bridge_address,
            key,
            value,
            proof,
            _signers,
            signatures
        );

        // Decode RLP bytes
        RLPReader.RLPItem[] memory args = value.toRlpItem().toList();
        address target_address = args[0].toAddress();
        uint amount = args[1].toUint();
        uint nonce = args[2].toUint();

        // Unwraps must be finalized sequentially per target account
        uint old_nonce = unwrap_nonce[target_address];
        require(old_nonce + 1 == nonce, IBCF_Bridge_Error.INVALID_NONCE);
        // Increment nonce
        unwrap_nonce[target_address] = nonce;

        // Transfer tokens
        asset.transfer(target_address, amount);

        emit Unwrap(target_address, amount, nonce);
    }
}
