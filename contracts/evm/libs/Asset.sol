// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title ERC20Mintable
 * @dev ERC20 minting logic
 */
contract Asset is ERC20 {
    address manager;

    constructor(string memory name, string memory symbol, address _manager) ERC20(name, symbol) {
        manager = _manager;
    }

    /**
     * Modifier to check if caller is the manager
     */
    modifier is_manager() {
        require(msg.sender == manager, "NOT_MANAGER");
        _;
    }

    /**
     * Configure manaher
     */
    function set_manager(address _manager) public is_manager {
        manager = _manager;
    }

    /**
     * @dev Returns the number of decimals used to get its user representation.
     * For example, if `decimals` equals `2`, a balance of `505` tokens should
     * be displayed to a user as `5.05` (`505 / 10 ** 2`).
     *
     * Tokens usually opt for a value of 18, imitating the relationship between
     * Ether and Wei. This is the value {ERC20} uses, unless this function is
     * overridden;
     *
     * NOTE: This information is only used for _display_ purposes: it in
     * no way affects any of the arithmetic of the contract, including
     * {IERC20-balanceOf} and {IERC20-transfer}.
     */
    function decimals() public view virtual override returns (uint8) {
        return 12;
    }

    /**
     * @dev Function to mint tokens to address
     * @param account The account to mint tokens.
     * @param value The amount of tokens to mint.
     * @return A boolean that indicates if the operation was successful.
     */
    function mint(address account, uint256 value) public is_manager returns (bool) {
        _mint(account, value);
        return true;
    }

    /**
     * @dev Function to burn tokens to address
     * @param account The account to burn tokens from.
     * @param value The amount of tokens to burned.
     * @return A boolean that indicates if the operation was successful.
     */
    function burn(address account, uint256 value) public is_manager returns (bool) {
        _burn(account, value);
        return true;
    }
}
