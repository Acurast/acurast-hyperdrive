// SPDX-License-Identifier: MIT
// --------------------------------------------------------------------------
// This contract is an example of an acurast consumer on an EVM chain.
//
// It allows contracts to receive job fulfillments from Acurast processors.
// ---------------------------------------------------------------------------
pragma solidity ^0.8.17;

interface IAcurastConsumer {
    function fulfill(uint128 job_id, bytes memory payload) external;
}

contract BaseAcurastConsumer is IAcurastConsumer {
    address gateway;

    constructor(address proxy_gateway) {
        gateway = proxy_gateway;
    }


    /**
     * Modifier to check if caller is the manager
     */
    modifier is_gateway() {
        require(msg.sender == gateway, "NOT_ACURAST_GATEWAY");
        _;
    }


    function fulfill(uint128 job_id, bytes memory payload) public is_gateway {
        // Process payload
    }
}
