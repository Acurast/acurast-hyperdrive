// SPDX-License-Identifier: MIT
// -----------------------------------------------------------------------------
// This contract implements a crowdfunding blueprint for a cross-chain protocol.
// -----------------------------------------------------------------------------
pragma solidity ^0.8.17;

contract IBCF_Crowdfunding {
    uint counter;
    // Proof slots
    mapping(uint => address) funder_registry;
    mapping(uint => uint) amount_registry;

    event Funding(address funder, uint amount, uint nonce);

    /**
     * @dev Participate in a crowdfunding on Tezos with Ether.
     */
    receive() external payable {
        // Update registry (The registry is used for proof generation)
        counter += 1;
        funder_registry[counter] = msg.sender;
        amount_registry[counter] = msg.value;

        emit Funding(msg.sender, msg.value, counter);
    }
}
