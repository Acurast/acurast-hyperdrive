// SPDX-License-Identifier: MIT
// -----------------------------------------------------------------------------
// This contract implements a crowdfunding blueprint for a cross-chain protocol.
// -----------------------------------------------------------------------------
pragma solidity ^0.8.17;

contract IBCF_Crowdfunding {
    address payable recipient;
    uint counter;
    // Proof slots
    mapping(uint => address) funder_registry;
    mapping(uint => uint) amount_registry;

    constructor(address payable _recipient) {
        recipient = _recipient;
    }

    event Funding(address funder, uint amount, uint nonce);

    /**
     * @dev Participate in a crowdfunding on Tezos with Ether.
     */
    receive() external payable {
        // Update registry (The registry is used for proof generation)
        counter += 1;
        funder_registry[counter] = msg.sender;
        amount_registry[counter] = msg.value;

        // Send amount to the crowdfunding recipient
        recipient.transfer(msg.value);

        // Emit event
        emit Funding(msg.sender, msg.value, counter);
    }
}
