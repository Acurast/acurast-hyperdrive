const IBCF_Client = artifacts.require('IBCF_Client');
const IBCF_Validator = artifacts.require('IBCF_Validator');

const administrator = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0";
const tezos_packed_address = "0x050a0000001601688594334ba2fc87f986b2d0f327888b2baa143f00"
const tezos_chain_id = "0xaf1864d9"

module.exports = async function(deployer, _network, _accounts) {
    await deployer.deploy(IBCF_Validator, administrator, 1, tezos_chain_id);
    await deployer.deploy(IBCF_Client, IBCF_Validator.address, tezos_packed_address);
};
