// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

// --------------------------------------------------------------------------
// This contract implements the bridging protocol.
//
// It allows user to wrap Ethereum assets on the Tezos blockchain.
// --------------------------------------------------------------------------

import "../libs/RLPReader.sol";
import {IBCF_Validator} from "../IBCF_Validator.sol";
import "./MintableERC20.sol";

library IBCF_Bridge_Error {
    string constant INVALID_COUNTER = "INVALID_COUNTER";
}

contract IBCF_Bridge {
    IBCF_Validator validator;
    MintableERC20 asset;
    bytes tezos_bridge_address;
    mapping(bytes => uint) tezos_nonce; // Tezos address => nonce
    mapping(address => uint) eth_nonce; // Eth address => nonce
    mapping(bytes => bytes) registry; // (Tezos address + nonce) RLP encoded => amount RLP encoded

    using RLPReader for RLPReader.RLPItem;
    using RLPReader for bytes;

    constructor(IBCF_Validator _validator, MintableERC20 _asset, bytes memory _tezos_bridge_address) {
        validator = _validator;
        asset = _asset;
        tezos_bridge_address = _tezos_bridge_address;
    }

    function teleport(bytes memory target_address, uint amount) public {
        // Transfer assets
        asset.transferFrom(msg.sender, address(this), amount);

        uint nonce = tezos_nonce[target_address];
        tezos_nonce[target_address] = nonce + 1;
        registry[abi.encodePacked(target_address, nonce)] = abi.encodePacked(amount);
    }

    function receive_teleport(
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
        uint counter = args[2].toUint();

        // Teleports must be finalized sequentially per target account
        uint old_counter = eth_nonce[target_address];
        require(old_counter + 1 == counter, IBCF_Bridge_Error.INVALID_COUNTER);
        // Increment counter
        eth_nonce[target_address] = counter;

        // Transfer tokens
        asset.transfer(target_address, amount);
    }


    /**
     * Get the nonce of a given account.
     */
    function nonce_of(address account) public view returns (uint) {
        return eth_nonce[account];
    }
}
