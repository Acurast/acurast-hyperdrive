// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {EllipticCurve} from "./secp256r1.sol";

library Err {
    string constant NOT_ADMIN = "NOT_ADMIN";
    string constant PROOF_INVALID = "PROOF_INVALID";
    string constant NOT_ALLOWED = "NOT_ALLOWED";
    string constant SIGNATURE_INVALID = "SIGNATURE_INVALID";
}

contract IBCF_Validator {
    address private administrator;
    uint[2] private administrator_public_key;
    mapping(uint256 => bytes32) root_history;

    constructor(address _administrator, uint[2] memory _administrator_public_key) {
        administrator = _administrator;
        administrator_public_key = _administrator_public_key;
    }

    // modifier to check if caller is the administrator
    modifier isAdmin() {
        require(msg.sender == administrator, Err.NOT_ADMIN);
        _;
    }

    function update_administrator(address new_admnistrator, uint[2] memory new_administrator_public_key) public isAdmin {
        administrator = new_admnistrator;
        administrator_public_key = new_administrator_public_key;
    }

    function submit_merkle_root_restricted(uint256 level, bytes32 merkle_root) public isAdmin {
        root_history[level] = merkle_root;
    }

    function submit_merkle_root(uint256 level, bytes32 merkle_root, uint[2] memory rs /* Signature */) public view {
        bytes32 content_hash = sha256(abi.encodePacked(level, merkle_root));
        require(EllipticCurve.validateSignature(content_hash, rs, administrator_public_key), Err.SIGNATURE_INVALID);
    }

    // TODO: Remove in favor of secp256r1
    function add_merkle_root(uint256 level, bytes32 merkle_root, uint8 v, bytes32 r, bytes32 s) public {
        // Encode and hash the payload (it is used to validate the signature)
        bytes memory prefix = "\x19Ethereum Signed Message:\n";
        bytes memory content = abi.encodePacked(level, merkle_root);
        bytes32 hash = keccak256(abi.encodePacked(prefix, Utils.string_of_uint(content.length), content));
        // Make sure the contents were authorized by the administrator
        verify_signature(hash, v, r, s);

        root_history[level] = merkle_root;
    }

    function verify_proof(uint block_level, bytes memory owner, bytes memory key, bytes memory value, bytes32[2][] memory proof) public view {
        bytes32 hash = keccak256(abi.encodePacked(owner, key, value)); // starts with state_hash
        for (uint i=0; i<proof.length; i++) {
            if(proof[i][0] == 0x0) {
                hash = keccak256(abi.encodePacked(hash, proof[i][1]));
            } else {
                hash = keccak256(abi.encodePacked(proof[i][0], hash));
            }
        }
        require(root_history[block_level] == hash, Err.PROOF_INVALID);
    }

    function verify_signature(bytes32 hash, uint8 v, bytes32 r, bytes32 s) private view {
        return require(ecrecover(hash, v, r, s) == administrator, Err.NOT_ALLOWED);
    }
}

library Utils {
    function string_of_uint(uint256 value) internal pure returns (string memory) {
        // @credits https://github.com/OpenZeppelin/openzeppelin-contracts/blob/d50e608a4f0a74c75715258556e131a8e7e00f2d/contracts/utils/Strings.sol

        if (value == 0) {
            return "0";
        }
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}
