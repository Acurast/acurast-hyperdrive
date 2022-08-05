// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {IBCF_Validator} from "./IBCF_Validator.sol";

contract IBCF_Client {
    string counter = "0";
    bytes tezos_source;
    address validator_address;

    constructor(address _validator_address, bytes memory source) {
        validator_address = _validator_address;
        tezos_source = source;
    }

    function set_tezos_source(bytes memory source) public {
        tezos_source = source;
    }

    function set_counter(string memory _counter) public {
        counter = _counter;
    }

    function confirm_ping(
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

        uint _counter = Utils.uint_of_string(counter) + 1;
        require(_counter % 2 == 1, "EXPECTED_ODD_COUNTER");

        require(keccak256(key) == keccak256(bytes("counter")), "key must be counter");

        string memory payload = Utils.string_of_bytes(value);
        require(Utils.uint_of_string(payload) == _counter, "invalid counter");

        counter = Utils.string_of_uint(_counter);
    }

    function pong() public {
        uint _counter = Utils.uint_of_string(counter) + 1;
        require(_counter % 2 == 0, "EXPECTED_EVEN_COUNTER");

        counter = Utils.string_of_uint(_counter);
    }
}

library Utils {
    function string_of_bytes(bytes memory b) internal pure returns(string memory) {
        return string(b);
    }
    function string_of_uint(uint value) internal pure returns (string memory) {
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

    function uint_of_string(string memory value) internal pure returns (uint) {
        bytes memory b = bytes(value);
        uint result = 0;
        for (uint i = 0; i < b.length; i++) {
            if (b[i] >= byte(uint8(48)) && b[i] <= byte(uint8(57))) {
                result = result * 10 + (uint8(b[i]) - 48);
            }
        }
        return result;
    }
}
