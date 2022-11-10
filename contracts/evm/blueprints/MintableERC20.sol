// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.7.6;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title ERC20Mintable
 * @dev ERC20 minting logic
 */
contract MintableERC20 is ERC20 {
    address private minter;

    // modifier to check if caller is the minter
    modifier is_minter() {
        require(msg.sender == minter, "NOT_MINTER");
        _;
    }

    constructor(string memory name, string memory symbol, address _minter) ERC20(name, symbol) {
        minter = _minter;
    }

    /**
     * @dev Function to mint tokens to address
     * @param account The account to mint tokens.
     * @param value The amount of tokens to mint.
     * @return A boolean that indicates if the operation was successful.
     */
    function mint(address account, uint256 value) public is_minter returns (bool) {
        _mint(account, value);
        return true;
    }
}
