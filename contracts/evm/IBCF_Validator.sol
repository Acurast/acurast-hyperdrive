// SPDX-License-Identifier: MIT
// --------------------------------------------------------------------------
// This contract validates proofs generated from a Tezos smart-contract.
//
// More info: https://eips.ethereum.org/EIPS/eip-1186
// ---------------------------------------------------------------------------
pragma solidity 0.7.6;

import {EllipticCurve} from "./secp256r1.sol";

library Err {
    string constant NOT_ADMIN = "NOT_ADMIN";
    string constant PROOF_INVALID = "PROOF_INVALID";
    string constant MERKLE_ROOT_INVALID = "MERKLE_ROOT_INVALID";
    string constant NOT_ALLOWED = "NOT_ALLOWED";
    string constant SIGNATURE_INVALID = "SIGNATURE_INVALID";
    string constant SIGNER_EXISTS = "SIGNER_EXISTS";
}

contract IBCF_Validator {
    address private administrator;
    uint8 signatures_threshold;
    bytes tezos_chain_id;
    address[] private signers;
    mapping(address => uint[2]) signer_public_key;

    constructor(address _administrator, uint8 _signatures_threshold, bytes memory _tezos_chain_id) {
        administrator = _administrator;
        signatures_threshold = _signatures_threshold;
        tezos_chain_id = _tezos_chain_id;
    }

    // modifier to check if caller is the administrator
    modifier is_admin() {
        require(msg.sender == administrator, Err.NOT_ADMIN);
        _;
    }

    function update_administrator(address new_admnistrator) public is_admin {
        administrator = new_admnistrator;
    }

    function update_signatures_threshold(uint8 _signatures_threshold) public is_admin {
        signatures_threshold = _signatures_threshold;
    }

    function add_signers(address[] memory _signers, uint[2][] memory _signer_public_key) public is_admin {
        for (uint i=0; i<_signers.length; i++) {
            // Fail if signer already exists
            require(signer_public_key[_signers[i]][0] == 0, Err.SIGNER_EXISTS);
            // Add signer
            signers.push(_signers[i]);
            signer_public_key[_signers[i]] = _signer_public_key[i];
        }
    }

    function remove_signers(address[] memory _signers) public is_admin {
        for (uint i=0; i<_signers.length; i++) {
            for(uint j=0; j<signers.length; j++) {
                if(signers[j] == _signers[i]) {
                    delete signers[j];
                }
            }
            delete signer_public_key[_signers[i]];
        }
    }

    /**
     * Verifies that a given state exists on the Tezos blockchain at a given block.
     *
     * It first asserts that the block state was signed by at least X validators and
     * then validates the proof against the trusted block state.
     */
    function verify_proof(
        uint block_level,
        bytes32 merkle_root,
        bytes memory owner,
        bytes memory key,
        bytes memory value,
        bytes32[2][] memory proof,
        address[] memory _signers,
        uint[2][] memory signatures
    ) public view {
        // Validates the 'merkle_root' authenticity
        validate_merkle_root(block_level, merkle_root, _signers, signatures);

        bytes32 hash = keccak256(abi.encodePacked(owner, key, value)); // starts with state_hash
        for (uint i=0; i<proof.length; i++) {
            if(proof[i][0] == 0x0) {
                hash = keccak256(abi.encodePacked(hash, proof[i][1]));
            } else {
                hash = keccak256(abi.encodePacked(proof[i][0], hash));
            }
        }
        require(merkle_root == hash, Err.PROOF_INVALID);
    }

    /**
     * Validates the 'merkle_root' authenticity
     */
    function validate_merkle_root(
        uint block_level,
        bytes32 merkle_root,
        address[] memory _signers,
        uint[2][] memory signatures
    ) internal view {
        bytes32 content_hash = sha256(abi.encodePacked(tezos_chain_id, block_level, merkle_root));
        uint valid_signatures = 0;

        // Revert transaction if any signer is repeated
        validate_signers(_signers);

        for (uint i=0; i<signatures.length; i++) {
            if(validate_signature(content_hash, _signers[i], signatures[i])) {
                valid_signatures += 1;
            }
        }
        require(valid_signatures >= signatures_threshold, Err.MERKLE_ROOT_INVALID);
    }

    /**
     * Revert transaction if any signer is repeated
     */
    function validate_signers(address[] memory _signers) internal pure {
        for (uint i=0; i<_signers.length; i++) {
            for (uint j=i+1; j<_signers.length; j++) {
                if(_signers[i] == _signers[j]) {
                    revert();
                }
            }
        }
    }

    function validate_signature(bytes32 content_hash, address signer, uint[2] memory rs /* Signature */) internal view returns(bool) {
        return EllipticCurve.validateSignature(content_hash, rs, signer_public_key[signer]);
    }
}
