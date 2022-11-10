const { signContent, buildBuffer, createSecp256r1KeyPair, expectsFailure } = require("./utils");

const IBCF_Client = artifacts.require('IBCF_Client');
const IBCF_Validator = artifacts.require('IBCF_Validator');

let [public_key, pemFormattedKeyPair] = createSecp256r1KeyPair();

contract('IBCF_Client', async ([_, primary]) => {
    const signer_address = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0";
    const chain_id = "0xaf1864d9"
    const packed_tezos_client_address = "0x050a000000160000eaeec9ada5305ad61fc452a5ee9f7d4f55f80467";
    let client;
    let validator;

    beforeEach('Deploy contracts', async () => {
        validator = await IBCF_Validator.new(primary, 1, chain_id, { from: primary })
        client = await IBCF_Client.new(validator.address, packed_tezos_client_address, { from: primary })

        // Add signers
        await validator.add_signers([signer_address], [public_key], { from: primary })

        // Set counter
        await client.set_counter("0", { from: primary })
    })

    it('Call pong (Counter invalid)', async function() {
        expectsFailure(async () => await client.pong(), "Expected fail from wrong counter.");
    });

    it('Call confirm_ping (Valid proof)', async function() {
        const level = 1;
        const valid_merkle_root = "0x03fb6489062fe9474620ba4a55debfc6cbc295aefe4696999267402a2e8d54c1";
        const signature = signContent(pemFormattedKeyPair, buildBuffer(chain_id, level, valid_merkle_root));

        const signatures = [
            signature
        ];

        const proof = [
            ["0x0000000000000000000000000000000000000000000000000000000000000000", "0xee92f395cb07c5f75880971a8303899f9bdd71c9a15e3df3c755d946a65226f0"],
            ["0x0000000000000000000000000000000000000000000000000000000000000000", "0xcaf65ad810916d8806b6489cf56b2a92cb6497e3e63cfdf8987066b60bb8151d"],
            ["0x7149b45c8811e303bdafc8bac168ff42aeee1908705fb025ef454b7a5121fc17", "0x0000000000000000000000000000000000000000000000000000000000000000"],
            ["0x74220814f5b91d9b71bcce3950557719b4fa2634f1535e32f0e57e2174846dd1", "0x0000000000000000000000000000000000000000000000000000000000000000"],
            ["0x0000000000000000000000000000000000000000000000000000000000000000", "0x5e799ae27bc21362ef510ea126403823afbab41bf15bef8fe71d5be51ccd5496"],
            ["0x0000000000000000000000000000000000000000000000000000000000000000", "0xb71f9a155c40787bffbeac19861f3dd2f5f948282c1dd64f3b15904182a2f05a"]
        ];

        const key = "0x636f756e746572";
        const value = "0x31";
        await client.confirm_ping(level, valid_merkle_root, key, value, proof, [signer_address], signatures);
        // Test pong
        await client.pong();
    })
})
