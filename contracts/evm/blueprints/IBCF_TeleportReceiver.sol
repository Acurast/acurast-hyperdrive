// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

// --------------------------------------------------------------------------
// This contract implements the receiving end of an asset teleporting
// protocol, which uses Merkle proofs to validate the synchronization
// between chains.
// --------------------------------------------------------------------------

import "../libs/RLPReader.sol";
import {IBCF_Validator} from "../IBCF_Validator.sol";
import "./MintableERC20.sol";

library IBCF_TeleportReceiver_Error {
    string constant INVALID_COUNTER = "INVALID_COUNTER";
}

contract IBCF_TeleportReceiver {
    IBCF_Validator validator;
    MintableERC20 asset = MintableERC20(0);
    bytes tezos_teleporter;
    address admin;
    mapping(address => uint) registry;

    using RLPReader for RLPReader.RLPItem;
    using RLPReader for bytes;

    // modifier to check if caller is the administrator
    modifier is_admin() {
        require(msg.sender == admin, "NOT_ADMIN");
        _;
    }

    constructor(IBCF_Validator _validator, address _admin, bytes memory _tezos_teleporter) {
        validator = _validator;
        admin = _admin;
        tezos_teleporter = _tezos_teleporter;
    }

    function set_asset(MintableERC20 _asset) public is_admin {
        require(asset == MintableERC20(0), "ASSET_ALREADY_SET");
        asset = _asset;
    }

    function finalize_teleport(
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
            tezos_teleporter,
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
        uint old_counter = registry[target_address];
        require(old_counter + 1 == counter, IBCF_TeleportReceiver_Error.INVALID_COUNTER);
        // Increment counter
        registry[target_address] = counter;

        // Mint tokens
        asset.mint(target_address, amount);
    }

    /**
     * Get the nonce of a given account.
     */
    function nonce_of(address account) public view returns (uint) {
        return registry[account];
    }
}
