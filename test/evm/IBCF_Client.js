const { signContent, buildBuffer , createSecp256r1KeyPair} = require("./utils");
const crypto = require('crypto');
const ecPem  = require('ec-pem');

const IBCF_Client = artifacts.require('IBCF_Client');
const IBCF_Validator = artifacts.require('IBCF_Validator');

let [public_key, pemFormattedKeyPair] = createSecp256r1KeyPair();
const chain_id = "0xaf1864d9"

contract('IBCF_Client', async ([_, primary]) => {
    const signer_address = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0";
    const signer_public_key = ["0x80b156abc1b94075eb95ba6c397d50e987acf2bb8107dd1adb0c1691dee56bcb", "0x6379608d6db8f328b9e50f74778d2bf34d31e523ef4c72e8c2c7355264003f5a"];
    let client;
    let validator;
    beforeEach('deploy proof validator', async () => {
        validator = await IBCF_Validator.new(primary, 1, chain_id, { from: primary })
        client = await IBCF_Client.new(validator.address,"0x050a0000001601cf2a14662a31d76af69fe71ab045187b0965eb7600", { from: primary })

        // Add signers
        await validator.add_signers([signer_address], [signer_public_key], { from: primary })

        // Set counter
        await client.set_counter("4", { from: primary })
    })

    it('Call ping (Valid proof)', async function() {
        const level = 956480;
        const valid_merkle_root = "0x0fc1154b3a871e52ef7a03c6a45962609a45e0659b9fb1e391b9532d0465a9fb";
        //const signature = signContent(pemFormattedKeyPair, buildBuffer(chain_id, level, valid_merkle_root));
        const signatures = [
            [
              '0x00f149e30b7d45f15b02ac122e746a3e50e12df4b286c49809e26a06499fe28e91',
              '0x79c63076e4faf7c01ed83b39e1433dc92d6e797bed87af1c22f30272912d5e13'
            ]
        ]

        const proof = []

        const key = "0x636f756e746572";
        const value = "0x35";
        await client.ping(level, valid_merkle_root, key, value, proof, [signer_address], signatures);
    })
})
