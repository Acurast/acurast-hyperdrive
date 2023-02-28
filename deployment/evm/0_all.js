const fs = require("fs");

const IBCF_Validator = artifacts.require("IBCF_Validator");
const IBCF_Bridge = artifacts.require("IBCF_Bridge");
const IBCF_Crowdfunding = artifacts.require("IBCF_Crowdfunding");
const ERC20 = artifacts.require("MintableERC20");

const administrator = "0x3DF95B98abEA91975780646e344C8d14d512C95E";
const tezos_chain_id = "0xaf1864d9";

module.exports = async function (deployer, network, _accounts) {
  await deployer.deploy(IBCF_Validator, administrator, 1, tezos_chain_id, 5, [
    administrator,
  ]);
  const validator = await IBCF_Validator.deployed();

  const asset = await deployer.deploy(ERC20, "TEST", "TEST");
  const bridge = await deployer.deploy(
    IBCF_Bridge,
    validator.address,
    asset.address
  );

  const crowdfunding = await deployer.deploy(IBCF_Crowdfunding, administrator);

  const output =
    `IBCF_Validator: ${validator.address}\n` +
    `TEST_ERC20: ${asset.address}\n` +
    `IBCF_Bridge: ${bridge.address}\n` +
    `IBCF_Crowdfunding: ${crowdfunding.address}`;

  fs.writeFileSync(`__SNAPSHOTS__/evm-${network}-deployment.txt`, output, {
    encoding: "utf-8",
  });
};
