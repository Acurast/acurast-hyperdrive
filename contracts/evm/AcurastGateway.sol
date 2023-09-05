// SPDX-License-Identifier: MIT
// --------------------------------------------------------------------------
// This contract is used as a gateway to interact with the Acurast chain.
// ---------------------------------------------------------------------------
pragma solidity ^0.8.17;

import './MMR_Validator.sol';
import './AcurastConsumer.sol';
import './libs/Asset.sol';

library OUT_ACTION_KIND {
    uint16 constant REGISTER_JOB = 0;
    uint16 constant DEREGISTER_JOB = 1;
    uint16 constant FINALIZE_JOB = 2;

    uint16 constant NOOP = 255;
}

library IN_ACTION_KIND {
    uint16 constant ASSIGN_JOB_PROCESSOR = 0;
    uint16 constant FINALIZE_JOB = 1;

    uint16 constant NOOP = 255;
}

library JOB_STATUS {
    // Status after a job got registered.
    uint8 constant OPEN = 0;
    // Status after a valid match for a job got submitted.
    uint8 constant MATCHED = 1;
    // Status after all processors have acknowledged the job.
    uint8 constant ASSIGNED = 2;
    // Status when a job has been finalized or cancelled
    uint8 constant FINALIZED_OR_CANCELLED = 3;

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
    uint64 start_time;
    uint64 end_time;
    uint64 interval;
    bytes raw; //Abstract data, this field can be used to add new parameters to the job information structure after the contract has been deployed.
}

struct JobMatch {
    bytes32 source;
    uint64 start_delay;
}

struct JobRequirements {
    uint8 slots;
    uint128 reward;
    uint128 min_reputation;
    JobMatch[] instant_match;
}

struct JobSchedule {
    uint64 duration;
    uint64 start_time;
    uint64 end_time;
    uint64 interval;
    uint64 max_start_delay;
}

struct RegisterJobPayload {
    bytes32[] allowed_sources;
    bool allow_only_verified_sources;
    address destination;
    JobRequirements requirements;
    uint256 expected_fullfilment_fee;
    uint16[] required_modules;
    bytes script;
    JobSchedule schedule;
    uint32 memory_capacity;
    uint32 network_requests;
    uint32 storage_capacity;
}

struct AcurastJobRegistration {
    uint128 job_id;
    bytes32[] allowed_sources;
    bool allow_only_verified_sources;
    JobRequirements requirements;
    uint16[] required_modules;
    bytes script;
    JobSchedule schedule;
    uint32 memory_capacity;
    uint32 network_requests;
    uint32 storage_capacity;
}

struct Message {
    uint16 action;
    address origin;
    bytes payload;
}

struct MessageReceived {
    uint16 action;
    uint128 message_id;
    bytes payload;
}

/// Incoming action payloads

struct AssignJob {
    uint128 job_id;
    address processor;
}

struct FinalizeJob {
    uint128 job_id;
    uint256 unused_reward;
}

//! Incoming action payloads

struct UnhashedLeaf {
    // The leftmost index of a node
    uint256 k_index;
    // The position in the tree
    uint256 leaf_index;
    // The hash of the position in the tree
    bytes data;
}

struct ReceiveMessagesPayload {
    uint128 snapshot;
    uint256 mmr_size;
    UnhashedLeaf[] leaves;
    bytes32[] proof;
}

contract AcurastGatewayStorage {
    uint256 public out_seq_id;
    uint256 public in_seq_id;
    address public manager;
    MMR_Validator public proof_validator;
    Asset public acurast_asset;
    uint128 public job_seq_id;
    mapping(uint => JobInformation) job_information;
    mapping(uint => bytes32) message_hash;
    mapping(bytes32 => bytes) message;


    /**
     * Modifier to check if caller is the manager
     */
    modifier is_manager() {
        require(msg.sender == manager, "NOT_MANAGER");
        _;
    }

    /**
     * Configure acurast asset
     */
    function set_asset(Asset asset) public is_manager {
        acurast_asset = asset;
    }

    /**
     * Configure proof validator
     */
    function set_validator(MMR_Validator validator) public is_manager {
        proof_validator = validator;
    }

    /**
     * Configure manager
     */
    function set_manager(address _manager) public is_manager {
        manager = _manager;
    }
}


contract AcurastGateway is AcurastGatewayStorage {
    function initialize(MMR_Validator _proof_validator, address _manager) public {
        require(manager == address(0), "ALREADY_INITIALIZED");
        out_seq_id = 0;
        in_seq_id = 0;
        job_seq_id = 0;
        proof_validator = _proof_validator;
        manager = _manager;
    }
}

library Helper {
    function compute_execution_count(uint64 start_time, uint64 end_time, uint64 interval) internal pure returns (uint64) {
        require(start_time <= end_time, "INVALID_SCHEDULE");
        return (end_time - start_time) / interval;
    }

    function compute_maximum_fees(uint64 execution_count, uint16 slots, uint256 expected_fullfilment_fee) internal pure returns (uint256) {
        return slots * execution_count * expected_fullfilment_fee;
    }

    function compute_maximum_reward(uint64 execution_count, uint8 slots, uint256 reward_per_execution) internal pure returns (uint256) {
        return slots * execution_count * reward_per_execution;
    }
}

abstract contract IncomingActionHandler is AcurastGatewayStorage {
    event FeeSentToProcessor(uint128, address, uint256);
    event RefundJobCreator(uint128, uint256);

    function in_noop() internal {
        // DO NOTHING
    }

    function in_finalize_job(bytes memory payload) internal {
        // Decode action payload
        FinalizeJob memory action;
        (action) = abi.decode(payload, (FinalizeJob));

        // Assign processor to the job
        JobInformation memory job = job_information[action.job_id];

        // Update job status
        job.status = JOB_STATUS.FINALIZED_OR_CANCELLED;

        // Send unused fees to the job creator
        if(job.remaining_fee > 0) {
            (bool success,) = payable(job.creator).call{value: job.remaining_fee}("");
            // Emit an event if successful
            if(success) {
                emit RefundJobCreator(action.job_id, job.remaining_fee);
                job.remaining_fee = 0;
            }

            // Mint unused rewards back to the job creator
            require(action.unused_reward <= job.maximum_reward, "ABOVE_MAXIMUM_REWARD");
            acurast_asset.mint(job.creator, action.unused_reward);

            // Update job information
            job_information[action.job_id] = job;
        }
    }

    function in_assign_job_processor(bytes memory payload) internal {
        // Decode action payload
        AssignJob memory action;
        (action) = abi.decode(payload, (AssignJob));

        // Assign processor to the job
        job_information[action.job_id].processors.push(action.processor);

        // Send initial fees to the processor
        uint256 initial_fee = job_information[action.job_id].expected_fullfilment_fee;

        job_information[action.job_id].remaining_fee -= initial_fee;

        // Transfer amount
        (bool success,) = payable(action.processor).call{value: initial_fee}("");
        // Emit an event if successful
        if(success) {
            emit FeeSentToProcessor(action.job_id, action.processor, initial_fee);
        }

        // Updated job status
        if(job_information[action.job_id].processors.length == job_information[action.job_id].slots) {
            job_information[action.job_id].status = JOB_STATUS.ASSIGNED;
        }
    }
}

contract AcurastGatewayV2 is AcurastGatewayStorage, IncomingActionHandler {
    event ReceivedMessages(MessageReceived[]);
    event CouldNotProcessIncomingMessages(string, UnhashedLeaf[]);
    event CouldNotProcessIncomingMessages(bytes, UnhashedLeaf[]);

    /**
     * TODO: Remove for production
     * Mint Acurast tokens
     */
    function faucet(uint256 amount) public {
        acurast_asset.mint(msg.sender, amount);
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

    function noop() public {
        send_message(OUT_ACTION_KIND.NOOP, "");
    }

    /**
     * This function can be called by users to register Acurast jobs.
     */
    function register_job(RegisterJobPayload memory payload) public payable {
        // Increase job id sequence
        job_seq_id += 1;

        AcurastJobRegistration memory action = AcurastJobRegistration(
            job_seq_id,
            payload.allowed_sources,
            payload.allow_only_verified_sources,
            payload.requirements,
            payload.required_modules,
            payload.script,
            payload.schedule,
            payload.memory_capacity,
            payload.network_requests,
            payload.storage_capacity
        );

        // Get the number of times the job will execute
        uint64 execution_count = Helper.compute_execution_count(
            payload.schedule.start_time,
            payload.schedule.end_time,
            payload.schedule.interval
        );

        // Get the mamimum amount of rewards to be paid to the processors for executing the job
        uint256 maximum_reward = Helper.compute_maximum_reward(
            execution_count,
            payload.requirements.slots,
            payload.requirements.reward
        );

        // Burn tokens on the EVM side (The registration action will mint the tokens on Acurast)
        acurast_asset.burn(msg.sender, maximum_reward);

        // Get the expected fees to be paid to the processors and verify
        // if the sender provided enough balance to cover the costs
        uint256 expected_fee = Helper.compute_maximum_fees(
            execution_count,
            payload.requirements.slots,
            payload.expected_fullfilment_fee
        );
        require(msg.value == expected_fee, "INVALID_FEE_AMOUNT");

        address[] memory empty;
        JobInformation memory job_info = JobInformation(
            msg.sender, // job creator
            payload.destination,
            empty, // processors
            payload.expected_fullfilment_fee,
            expected_fee, // remaining_fee
            maximum_reward, // maximum_reward
            payload.requirements.slots,
            JOB_STATUS.OPEN, // status
            payload.schedule.start_time,
            payload.schedule.end_time,
            payload.schedule.interval,
            "" // raw bytes
        );
        // Store the jonb information
        job_information[job_seq_id] = job_info;

        send_message(OUT_ACTION_KIND.REGISTER_JOB, abi.encode(action));
    }

    /**
     * This function can be called by users to register Acurast jobs.
     */
    function deregister_job(uint128 job_id) public {
        JobInformation memory job = job_information[job_id];

        // Verify if job can be finalized
        require(job.status == JOB_STATUS.OPEN, "CANNOT_CANCEL_JOB");

        // Only the job creator can deregister the job
        address origin = msg.sender;
        require(job.creator == origin, "NOT_JOB_CREATOR");

        bytes memory encoded_payload = abi.encode(job_id);

        send_message(OUT_ACTION_KIND.DEREGISTER_JOB, encoded_payload);
    }

    /**
     * This function can be called by users to register Acurast jobs.
     */
    function finalize_job(uint128[] memory job_ids) public {
        for(uint i=0; i<job_ids.length; i++) {
            // Get job information
            JobInformation memory job = job_information[job_ids[i]];

            // Verify if job can be finalized
            bool is_open = job.status == JOB_STATUS.OPEN;
            bool is_expired = (job.end_time / 1000) < block.timestamp;

            require(is_open || is_expired, "CANNOT_FINALIZE_JOB");

            // Only the job creator can deregister the job
            require(job.creator == msg.sender, "NOT_JOB_CREATOR");
        }

        bytes memory encoded_payload = abi.encode(job_ids);

        send_message(OUT_ACTION_KIND.FINALIZE_JOB, encoded_payload);
    }

    function process_incoming_messages(MessageReceived[] memory messages) public returns (bool) {
        // This method can only be called by this contract
        require(msg.sender == address(this), "NOT_AUTHORIZED");

        for (uint i=0; i<messages.length; i++) {
            // Process actions by kind
            if (messages[i].action == IN_ACTION_KIND.NOOP) {
                // Explicitly do nothing
                IncomingActionHandler.in_noop();
            } if (messages[i].action == IN_ACTION_KIND.FINALIZE_JOB) {
                IncomingActionHandler.in_finalize_job(messages[i].payload);
            } else if (messages[i].action == IN_ACTION_KIND.ASSIGN_JOB_PROCESSOR) {
                IncomingActionHandler.in_assign_job_processor(messages[i].payload);
            }
        }

        return true;
    }

    function receive_messages(ReceiveMessagesPayload memory proof) public {
        MmrLeaf[] memory leaves = new MmrLeaf[](proof.leaves.length);
        MessageReceived[] memory messages = new MessageReceived[](proof.leaves.length);
        for (uint i=0; i<proof.leaves.length; i++) {
            UnhashedLeaf memory leave = proof.leaves[i];
            leaves[i] = MmrLeaf(leave.k_index, leave.leaf_index, keccak256(leave.data));

            MessageReceived memory message;
            (message) = abi.decode(leave.data, (MessageReceived));

            require(message.message_id == in_seq_id, "INVALID_MESSAGE_ID");
            in_seq_id += 1;
            messages[i] = message;
        }
        // Process messages
        // If the proof is invalid, it will be reverted at the end.
        try AcurastGatewayV2(this).process_incoming_messages(messages) returns (bool result) {
            emit ReceivedMessages(messages);
        } catch Error(string memory err) {
            // This may occur if there is an overflow with the two numbers and the `AddNumbers` contract explicitly fails with a `revert()`
            emit CouldNotProcessIncomingMessages(err, proof.leaves);
        } catch (bytes memory err) {
            emit CouldNotProcessIncomingMessages(err, proof.leaves);
        }

        // Validate messages proof, the whole call will revert if the proof is invalid.
        proof_validator.verify_proof(proof.snapshot, proof.proof, leaves, proof.mmr_size);
    }

    /**
     * Proxy job fulfillment to the respective destination and
     * re-fill the processor address with the execution fees.
     *
     * Also, ensure that the caller is a valid processor address.
     */
    function fulfill(uint128 job_id, bytes memory payload) public {
        // Verify if sender is assigned to the job
        require(contains_address(job_information[job_id].processors, msg.sender), "NOT_JOB_PROCESSOR");

        // Re-fill processor fees
        uint256 fee = job_information[job_id].expected_fullfilment_fee;
        job_information[job_id].remaining_fee -= fee;

        // Do not send a empty transaction
        if(job_information[job_id].expected_fullfilment_fee > 0) {
            // Transfer amount
            (bool success,) = payable(msg.sender).call{value: fee}("");
            // Emit an event if successful
            if(success) {
                emit FeeSentToProcessor(job_id, msg.sender, fee);
            }
        }

        // Pass fulfillment payload to target contract
        IAcurastConsumer(job_information[job_id].destination).fulfill(job_id, payload);
    }

    function contains_address(address[] memory processors, address processor) private pure returns (bool) {
        for(uint i=0; i<processors.length; i++) {
            if (processors[i] == processor) {
                return true;
            }
        }
        return false;
    }

    function get_message(uint256 message_id) public view returns(bytes memory) {
        return message[message_hash[message_id]];
    }

    function get_message_hash(uint256 message_id) public view returns(bytes32) {
        return message_hash[message_id];
    }

    function get_job_information(uint256 job_id) public view returns(JobInformation memory) {
        return job_information[job_id];
    }
}
