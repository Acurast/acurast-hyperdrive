// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {IBCF_Validator} from "./IBCF_Validator.sol";

contract IBCF_Client {
    uint msg_counter = 0;
    uint balance = 0;
    bytes tezos_source;
    address validator_address;

    constructor(address _validator_address, bytes memory source) {
        validator_address = _validator_address;
        tezos_source = source;
    }

    function set_tezos_source(bytes memory source) public {
        tezos_source = source;
    }

    function mint(
        uint block_level,
        bytes32 merkle_root,
        bytes memory key,
        bytes memory value,
        bytes32[2][] memory proof,
        address[] memory _signers,
        uint[2][] memory signatures
    ) public {
        IBCF_Validator(validator_address).verify_proof(
            block_level,
            merkle_root,
            tezos_source,
            key,
            value,
            proof,
            _signers,
            signatures
        );

        balance = 100;
    }

    function getBalance() public view returns (uint) {
        return balance;
    }
}
