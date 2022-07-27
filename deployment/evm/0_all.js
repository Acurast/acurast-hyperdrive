const IBCF_Client = artifacts.require('IBCF_Client');
const IBCF_Validator = artifacts.require('IBCF_Validator');

const administrator = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0";
const tezos_packed_address = "0x050a0000001601a33b174ba24455c3448887b7c3aa4daccc1fbe4d00"

module.exports = async function(deployer, _network, _accounts) {
    await deployer.deploy(IBCF_Validator, administrator, 1);
    await deployer.deploy(IBCF_Client, IBCF_Validator.address, tezos_packed_address);
};
