// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {IBCF_Validator} from "./IBCF_Validator.sol";

contract IBCF_Client {
    uint counter = 0;
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

        balance += bytesToUint(sliceBytes(value, 2));
        counter += 1;
    }

    function getBalance() public view returns (uint) {
        return balance;
    }

    function getCounter() public view returns (uint) {
        return counter;
    }

    function sliceBytes(bytes memory b, uint offset) public pure returns (bytes memory){
        bytes memory _bytes;
        for(uint i=offset;i<b.length;i++){
            _bytes = abi.encodePacked(_bytes, b[i]);
        }
        return _bytes;
    }

    function bytesToUint(bytes memory b) public pure returns (uint256){
        uint256 number;
        for(uint i=0;i<b.length;i++){
            number = number + uint8(b[i]);
        }
        return number;
    }

    function decodeNibbles(bytes memory compact, uint skipNibbles) public view returns (bytes memory nibbles) {
        require(compact.length > 0, "Empty bytes array");

        uint length = compact.length * 2;
        require(skipNibbles <= length, "Skip nibbles amount too large");
        length -= skipNibbles;

        nibbles = new bytes(length);
        uint nibblesLength = 0;

        for (uint i = skipNibbles; i < skipNibbles + length; i += 1) {
            if (i % 2 == 0) {
                nibbles[nibblesLength] = bytes1((uint8(compact[i/2]) >> 4) & 0xF);
            } else {
                nibbles[nibblesLength] = bytes1((uint8(compact[i/2]) >> 0) & 0xF);
            }
            nibblesLength += 1;
        }

        assert(nibblesLength == nibbles.length);
    }
}
