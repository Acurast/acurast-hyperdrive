const { createSecp256r1KeyPair, signContent, buildBuffer, expectsFailure } = require("../utils");

const IBCF_Bridge = artifacts.require('IBCF_Bridge');
const IBCF_Validator = artifacts.require('IBCF_Validator');
const ERC20 = artifacts.require('MintableERC20');

let [public_key, pemFormattedKeyPair] = createSecp256r1KeyPair();

contract('IBCF_Bridge', async ([_, primary]) => {
    const signer_address = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0";
    const chain_id = "0xaf1864d9";
    const tezos_bridge = "0x050a0000001601d1371b91c7491542e97deee96091e28a80b2335900";
    const tezos_address = "0x050a0000001601d1371b91c7491542e97deee96091e28a80b2335900";
    let bridge;
    let validator;
    let asset;

    before('Deploy contracts', async () => {
        validator = await IBCF_Validator.new(primary, 1, chain_id, { from: primary });
        asset = await ERC20.new("TOKEN", "ABC", primary, { from: primary });
        bridge = await IBCF_Bridge.new(validator.address, asset.address, { from: primary });

        // Fund accounts
        await asset.mint(primary, "10", { from: primary });

        // Add signers
        await validator.add_signers([signer_address], [public_key], { from: primary });
    })

    it('Call set_tezos_bridge_address', async function() {
        await bridge.set_tezos_bridge_address(tezos_bridge, { from: primary })

        await expectsFailure(async () => await bridge.set_tezos_bridge_address(tezos_bridge, { from: primary }), "Expected error (user must set the allowance).");
    });

    it('Call wrap', async function() {
        await expectsFailure(async () => await bridge.wrap(tezos_address, 10, { from: primary }), "Expected error (user must set the allowance).");

        await asset.approve(bridge.address, 10, { from: primary });
        await bridge.wrap(tezos_address, 10, { from: primary });
    });

    it('Call unwrap', async function() {
        const level = 1;
        const valid_merkle_root = "0x882f1702afb628fa5883b06c5a5f57dfded1a9d063bbd3bea8a59812b1f37a3f";
        const signature = signContent(pemFormattedKeyPair, buildBuffer(chain_id, level, valid_merkle_root));
        const target_address = "0x1111111111111111111111111111111111111111";

        const signatures = [
            signature
        ];

        const proof = [
            ["0x0000000000000000000000000000000000000000000000000000000000000000", "0x754d30463d4f6bd2aaaebbb04e5af504ce44ced91b586fbf6330591c2b3d581a"]
        ];

        const key = "0xd79411111111111111111111111111111111111111118101";
        const value = "0xd994111111111111111111111111111111111111111181098101";

        let account_nonce = await bridge.nonce_of(target_address);
        assert(account_nonce == 0);

        let account_balance = await asset.balanceOf(target_address);
        assert(account_balance == 0);

        await bridge.unwrap(level, valid_merkle_root, key, value, proof, [signer_address], signatures);

        account_nonce = await bridge.nonce_of("0x1111111111111111111111111111111111111111");
        assert(account_nonce == 1);

        account_balance = await asset.balanceOf(target_address);
        assert(account_balance == 9);

        // Cannot teleport the same proof twice
        await expectsFailure(async () => await bridge.unwrap(level, valid_merkle_root, key, value, proof, [signer_address], signatures), "Expected error (invalid nonce).");
    });
})
