const IBCF_Client = artifacts.require('IBCF_Client');
const IBCF_Validator = artifacts.require('IBCF_Validator');

const administrator = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0"

module.exports = function(deployer, _network, _accounts) {
    deployer.deploy(IBCF_Validator, administrator).then(() => { deployer.deploy(IBCF_Client, IBCF_Validator.address); });
};
