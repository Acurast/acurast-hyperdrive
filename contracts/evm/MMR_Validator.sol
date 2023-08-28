// SPDX-License-Identifier: Apache2
pragma solidity ^0.8.17;

import "./libs/MerkleMountainRange.sol";

library MMR_Validator_Err {
    string constant NOT_ADMIN = "NOT_ADMIN";
    string constant PROOF_INVALID = "PROOF_INVALID";
    string constant NOT_ALLOWED = "NOT_ALLOWED";
    string constant VALIDATOR_EXISTS = "VALIDATOR_EXISTS";
    string constant INVALID_SNAPSHOT = "INVALID_SNAPSHOT";
    string constant SNAPSHOT_NOT_FINALIZED = "SNAPSHOT_NOT_FINALIZED";
}

struct StateRootSubmission {
    address validator;
    bytes32 state_root;
}

contract MMR_Validator is MerkleMountainRange {
    uint256 current_snapshot = 1;
    address manager;
    // Minimum expected endorsements for a given state root to be considered valid
    uint8 minimum_endorsements;
    // The validator only stores the state roots of the latest `history_length` blocks
    uint16 history_length;
    uint[] history;
    address[] validators;
    mapping(uint256 => StateRootSubmission[]) snapshot;

    constructor(address _manager, uint8 _minimum_endorsements, uint16 _history_length, address[] memory _validators) {
        manager = _manager;
        minimum_endorsements = _minimum_endorsements;
        history_length = _history_length;

        // Add initial validators
        for (uint i=0; i<_validators.length; i++) {
            validators.push(_validators[i]);
        }
    }

    /**
     * Modifier to check if caller is the manager
     */
    modifier is_manager() {
        require(msg.sender == manager, MMR_Validator_Err.NOT_ADMIN);
        _;
    }

    /**
     * Modifier to check if caller is a validator
     */
    modifier is_validator() {
        for (uint i=0; i<validators.length; i++) {
            if(validators[i] == msg.sender) {
                _;
                return;
            }
        }
        revert(MMR_Validator_Err.NOT_ALLOWED);
    }


    function add_validators(address[] memory _validators) public is_manager {
        for (uint i=0; i<_validators.length; i++) {
            for (uint j=0; j<validators.length; j++) {
                // Validator must not exist.
                require(_validators[i] != validators[j], MMR_Validator_Err.VALIDATOR_EXISTS);
            }
            // Add validator
            validators.push(_validators[i]);
        }
    }

    function remove_validators(address[] memory _validators) public is_manager {
        for (uint i=0; i<_validators.length; i++) {
            for(uint j=0; j<validators.length; j++) {
                if(validators[j] == _validators[i]) {
                    delete validators[j];
                }
            }
        }
    }


    /**
     * Adds the state root for a given snapshot.
     */
    function submit_state_root(uint snapshot_number, bytes32 _state_root) public is_validator {
        // Ensure state roots are processed sequentially
        require(current_snapshot == snapshot_number, MMR_Validator_Err.INVALID_SNAPSHOT);

        // Add state root submission
        bool endorsed = false;
        for(uint i=0; i<snapshot[current_snapshot].length; i++) {
            // Override previous endorsement
            if (snapshot[current_snapshot][i].validator == msg.sender) {
                snapshot[current_snapshot][i].state_root =_state_root;
                endorsed = true;
                break;
            }
        }
        if (!endorsed) {
            snapshot[current_snapshot].push(StateRootSubmission(msg.sender, _state_root));
        }

        // Finalize state root submissions
        if (can_finalize_snapshot()) {
            history.push(current_snapshot);
            current_snapshot += 1;
        }

        // Remove old state root
        if(history.length > history_length) {
            uint oldest_index = 0;
            for (uint i=0; i<history.length; i++) {
                if(history[i] < history[oldest_index]) {
                    oldest_index = i;
                }
            }
            uint oldest_snapshot = history[oldest_index];
            delete history[oldest_index];
            delete snapshot[oldest_snapshot];
        }
    }


    /**
     * Verifies that a given state exists in an EVM source chain at a given block.
     *
     * It first asserts that the block state was signed by at least X validators and
     * then validates the proof against the trusted block state.
     */
    function verify_proof(uint128 snapshot_number, bytes32[] memory proof, MmrLeaf[] memory leaves, uint256 mmr_size) public view {
        bytes32 snapshot_root = get_state_root(snapshot_number);

        require(VerifyProof(snapshot_root, proof, leaves, mmr_size), MMR_Validator_Err.PROOF_INVALID);
    }

    /**
     * Get the most endorsed state root for a give snapshot.
     *
     * Fails if snapshot was not finalized.
     */
    function get_state_root(uint snapshot_number) public view returns (bytes32) {
        require(snapshot_number < current_snapshot, MMR_Validator_Err.SNAPSHOT_NOT_FINALIZED);

        StateRootSubmission[] memory submissions = snapshot[snapshot_number];

        // EVM does not support dynamic memory arrays :(
        bytes32[] memory unique_submissions = new bytes32[](submissions.length);
        uint8 uniques = 0;
        for (uint i=0; i<submissions.length; i++) {
            bool exists = false;
            for (uint j=0; j<unique_submissions.length; j++) {
                if (submissions[i].state_root == unique_submissions[j]) {
                    exists = true;
                }
            }
            if (!exists) {
                unique_submissions[uniques++] = submissions[i].state_root;
            }
        }

        uint8[] memory root_count = new uint8[](uniques);
        uint most_endorsed = 0;
        for (uint i=0; i<uniques; i++) {
            for (uint j=0; j<submissions.length; j++) {
                if (unique_submissions[i] == submissions[j].state_root) {
                    root_count[i] += 1;
                }
            }
            if (root_count[most_endorsed] < root_count[i]) {
                most_endorsed = i;
            }
        }

        return unique_submissions[most_endorsed];
    }

    /**
     * Verify if snapshot can be finalized.
     *
     * The snapshot cannot be finalized if:
     *  - The state root has not been endorsed at least `minimum_endorsements` times;
     *  - There are multiple most endorsed state roots.
     */
    function can_finalize_snapshot() internal view returns (bool) {
        StateRootSubmission[] memory submissions = snapshot[current_snapshot];

        // EVM does not support dynamic memory arrays :(
        bytes32[] memory unique_submissions = new bytes32[](submissions.length);
        uint8 uniques = 0;
        for (uint i=0; i<submissions.length; i++) {
            bool exists = false;
            for (uint j=0; j<unique_submissions.length; j++) {
                if (submissions[i].state_root == unique_submissions[j]) {
                    exists = true;
                }
            }
            if (!exists) {
                unique_submissions[uniques++] = submissions[i].state_root;
            }
        }

        uint8[] memory root_count = new uint8[](uniques);
        uint most_endorsed = 0;
        for (uint i=0; i<uniques; i++) {
            for (uint j=0; j<submissions.length; j++) {
                if (unique_submissions[i] == submissions[j].state_root) {
                    root_count[i] += 1;
                }
            }
            if (root_count[most_endorsed] < root_count[i]) {
                most_endorsed = i;
            }
        }

        // Make sure the root has enough endorsements
        bool has_enough_endorsements = root_count[most_endorsed] >= minimum_endorsements;

        // Make sure there is only one most endorsed root
        bool single_most_endorsed = true;
        for (uint i=0; i<uniques; i++) {
            if (most_endorsed != i && root_count[most_endorsed] == root_count[i]) {
                single_most_endorsed = false;
            }
        }

        return has_enough_endorsements && single_most_endorsed;
    }

    function get_history() public view returns (uint[] memory) {
        return history;
    }

    function get_current_snapshot() public view returns (uint) {
        return current_snapshot;
    }

    function get_current_snapshot_submissions() public view returns (StateRootSubmission[] memory) {
        return snapshot[current_snapshot];
    }
}
