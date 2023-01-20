const IBCF_Validator = artifacts.require("IBCF_Validator");
const IBCF_Bridge = artifacts.require("IBCF_Bridge");
const ERC20 = artifacts.require("MintableERC20");

const administrator = "0x3DF95B98abEA91975780646e344C8d14d512C95E";
const tezos_chain_id = "0xaf1864d9";

module.exports = async function (deployer, _network, _accounts) {
  await deployer.deploy(IBCF_Validator, administrator, 1, tezos_chain_id, 5, [
    administrator,
  ]);

  const validator = await IBCF_Validator.deployed();

  const asset = await deployer.deploy(ERC20, "TEST", "TEST", administrator);
  // Fund accounts
  await asset.mint(administrator, "1000000");

  await deployer.deploy(IBCF_Bridge, validator.address, asset.address);
};
