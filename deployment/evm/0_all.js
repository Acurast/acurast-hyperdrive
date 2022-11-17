const IBCF_Client = artifacts.require('IBCF_Client');
const IBCF_Validator = artifacts.require('IBCF_Validator');
const IBCF_Bridge = artifacts.require('IBCF_Bridge');
const ERC20 = artifacts.require('MintableERC20');

const administrator = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0";
const administrator_public_key = ["0x80b156abc1b94075eb95ba6c397d50e987acf2bb8107dd1adb0c1691dee56bcb", "0x6379608d6db8f328b9e50f74778d2bf34d31e523ef4c72e8c2c7355264003f5a"];
const tezos_packed_address = "0x050a0000001601cf2a14662a31d76af69fe71ab045187b0965eb7600"
const tezos_chain_id = "0xaf1864d9"

module.exports = async function(deployer, _network, _accounts) {
    await deployer.deploy(IBCF_Validator, administrator, 1, tezos_chain_id);

    // Add signers
    console.log("\nAdd signers\n")
    const validator = await IBCF_Validator.deployed();
    await validator.add_signers(
        [administrator],
        [administrator_public_key]
    );

    await deployer.deploy(IBCF_Client, validator.address, tezos_packed_address);

    const asset = await deployer.deploy(ERC20, "TEST", "TEST", administrator);
    // Fund accounts
    await asset.mint(administrator, "1000000");

    await deployer.deploy(IBCF_Bridge, validator.address, asset.address, tezos_packed_address);
};
