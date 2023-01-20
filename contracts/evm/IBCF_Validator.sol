// SPDX-License-Identifier: MIT
// --------------------------------------------------------------------------
// This contract validates proofs generated from a Tezos smart-contract.
//
// More info: https://eips.ethereum.org/EIPS/eip-1186
// ---------------------------------------------------------------------------
pragma solidity ^0.8.17;

library Err {
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

struct Snapshot {
    uint snapshot_number;
    bytes32 merkle_root;
}

contract IBCF_Validator {
    uint current_snapshot = 1;
    address administrator;
    // Minimum expected endorsements for a given state root to be considered valid
    uint8 minimum_endorsements;
    // The validator only stores the state roots of the latest `history_length` blocks
    uint16 history_length;
    bytes tezos_chain_id;
    uint[] history;
    address[] validators;
    mapping(uint => StateRootSubmission[]) state_root;

    constructor(address _administrator, uint8 _minimum_endorsements, bytes memory _tezos_chain_id, uint16 _history_length, address[] memory _validators) {
        administrator = _administrator;
        minimum_endorsements = _minimum_endorsements;
        tezos_chain_id = _tezos_chain_id;
        history_length = _history_length;

        // Add initial validators
        for (uint i=0; i<_validators.length; i++) {
            validators.push(_validators[i]);
        }
    }

    /**
     * Modifier to check if caller is the administrator
     */
    modifier is_admin() {
        require(msg.sender == administrator, Err.NOT_ADMIN);
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
        revert(Err.NOT_ALLOWED);
    }

    function update_administrator(address new_admnistrator) public is_admin {
        administrator = new_admnistrator;
    }

    function update_minimum_endorsements(uint8 _minimum_endorsements) public is_admin {
        minimum_endorsements = _minimum_endorsements;
    }

    function add_validators(address[] memory _validators) public is_admin {
        for (uint i=0; i<_validators.length; i++) {
            for (uint j=0; j<validators.length; j++) {
                // Validator must not exist.
                require(_validators[i] != validators[j], Err.VALIDATOR_EXISTS);
            }
            // Add validator
            validators.push(_validators[i]);
        }
    }

    function remove_validators(address[] memory _validators) public is_admin {
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
        require(current_snapshot == snapshot_number, Err.INVALID_SNAPSHOT);

        // Add state root submission
        bool endorsed = false;
        for(uint i=0; i<state_root[current_snapshot].length; i++) {
            // Override previous endorsement
            if (state_root[current_snapshot][i].validator == msg.sender) {
                state_root[current_snapshot][i].state_root =_state_root;
                endorsed = true;
                break;
            }
        }
        if (!endorsed) {
            state_root[current_snapshot].push(StateRootSubmission(msg.sender, _state_root));
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
            delete state_root[oldest_snapshot];
        }
    }

    /**
     * Verifies that a given state exists on the Tezos blockchain at a given block.
     *
     * It first asserts that the block state was signed by at least X validators and
     * then validates the proof against the trusted block state.
     */
    function verify_proof(
        uint snapshot_number,
        bytes memory owner,
        bytes memory key,
        bytes memory value,
        bytes32[2][] memory proof
    ) public view {
        bytes32 hash = keccak256(abi.encodePacked(owner, key, value)); // starts with state_hash
        for (uint i=0; i<proof.length; i++) {
            if(proof[i][0] == 0x0) {
                hash = keccak256(abi.encodePacked(hash, proof[i][1]));
            } else {
                hash = keccak256(abi.encodePacked(proof[i][0], hash));
            }
        }
        require(get_state_root(snapshot_number) == hash, Err.PROOF_INVALID);
    }

    /**
     * Get the most endorsed state root for a give snapshot.
     *
     * Fails if snapshot was not finalized.
     */
    function get_state_root(uint snapshot_number) public view returns (bytes32) {
        require(snapshot_number < current_snapshot, Err.SNAPSHOT_NOT_FINALIZED);

        StateRootSubmission[] memory submissions = state_root[snapshot_number];

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
        StateRootSubmission[] memory submissions = state_root[current_snapshot];

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
        return state_root[current_snapshot];
    }
}
