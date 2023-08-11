// SPDX-License-Identifier: MIT
// --------------------------------------------------------------------------
// This contract is used as a gateway to interact with the Acurast chain.
// ---------------------------------------------------------------------------
pragma solidity ^0.8.17;

library OUT_ACTION_KIND {
    uint16 constant REGISTER_JOB = 0;
    uint16 constant DEREGISTER_JOB = 1;
    uint16 constant FINALIZE_JOB = 2;
}

struct JobInformation {
    address creator;
    address destination;
    address[] processors;
    uint256 expected_fullfilment_fee;
    uint256 remaining_fee;
    uint256 maximum_reward;
    uint256 slots;
    uint8 status; // 0 - Submitted, 1 - Assigned, 2 - Finalized/Cancelled,
    uint64 startTime;
    uint64 endTime;
    uint64 interval;
    bytes raw; //Abstract data, this field can be used to add new parameters to the job information structure after the contract has been deployed.
}

struct JobMatch {
    bytes32 source;
    uint64 startDelay;
}

struct JobRequirements {
    uint8 slots;
    uint128 reward;
    uint128 minReputation;
    JobMatch[] instantMatch;
}

struct JobSchedule {
    uint64 duration;
    uint64 startTime;
    uint64 endTime;
    uint64 interval;
    uint64 maxStartDelay;
}

struct RegisterJobPayload {
    bytes32[] allowedSources;
    bool allowOnlyVerifiedSources;
    address destination;
    JobRequirements requirements;
    uint256 expectedFulfillmentFee;
    uint16[] requiredModules;
    bytes script;
    JobSchedule schedule;
    uint32 memoryCapacity;
    uint32 networkRequests;
    uint32 storageCapacity;
}

struct AcurastJobRegistration {
    uint128 jobId;
    bytes32[] allowedSources;
    bool allowOnlyVerifiedSources;
    JobRequirements requirements;
    uint16[] requiredModules;
    bytes script;
    JobSchedule schedule;
    uint32 memoryCapacity;
    uint32 networkRequests;
    uint32 storageCapacity;
}

struct Message {
    uint16 action;
    address origin;
    bytes payload;
}

contract AcurastGatewayStorage {
    uint256 out_seq_id;
    uint256 in_seq_id;
    address proof_validator;
    uint128 job_seq_id;
    mapping(uint => JobInformation) job_information;
    mapping(uint => bytes32) message_hash;
    mapping(bytes32 => bytes) message;
}


contract AcurastGateway is AcurastGatewayStorage {
    function initialize() public {
        out_seq_id = 0;
        in_seq_id = 0;
        job_seq_id = 0;
    }

    /**
     * Send outgoing action
     */
    function send_message(uint16 kind, bytes memory encoded_payload) private {
        // Increase sequential identifier
        out_seq_id += 1;

        // Encode action
        bytes memory encoded_msg = abi.encode(Message(kind, msg.sender, encoded_payload));

        // Commit action
        bytes32 h = keccak256(encoded_msg);
        message_hash[out_seq_id] = h;
        message[h] = encoded_msg;
    }

    /**
     * This function can be called by users to register Acurast jobs.
     */
    function register_job(RegisterJobPayload memory payload) public {
        // Increase job id sequence
        job_seq_id += 1;

        AcurastJobRegistration memory action = AcurastJobRegistration(
            job_seq_id,
            payload.allowedSources,
            payload.allowOnlyVerifiedSources,
            payload.requirements,
            payload.requiredModules,
            payload.script,
            payload.schedule,
            payload.memoryCapacity,
            payload.networkRequests,
            payload.storageCapacity
        );

        send_message(OUT_ACTION_KIND.REGISTER_JOB, abi.encode(action));
    }

    /**
     * This function can be called by users to register Acurast jobs.
     */
    function deregister_job(uint128 job_id) public {
        bytes memory encoded_payload = abi.encode(job_id);

        send_message(OUT_ACTION_KIND.DEREGISTER_JOB, encoded_payload);
    }

    /**
     * This function can be called by users to register Acurast jobs.
     */
    function finalize_job(uint128[] memory job_ids) public {
        bytes memory encoded_payload = abi.encode(job_ids);

        send_message(OUT_ACTION_KIND.FINALIZE_JOB, encoded_payload);
    }

    function get_message(uint256 message_id) public view returns(bytes memory) {
        return message[message_hash[message_id]];
    }
}
