const { createSecp256r1KeyPair, signContent, buildBuffer, expectsFailure } = require("../utils");

const IBCF_Bridge = artifacts.require('IBCF_Bridge');
const IBCF_Validator = artifacts.require('IBCF_Validator');
const ERC20 = artifacts.require('MintableERC20');

let [public_key, pemFormattedKeyPair] = createSecp256r1KeyPair();

contract('IBCF_Bridge', async ([_, primary]) => {
    const signer_address = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0";
    const chain_id = "0xaf1864d9";
    const tezos_teleport = "0x050a0000001601d1371b91c4cf72f705512fdf3eda99ca70af9f4800";
    const tezos_address = "0x1601d1371b91c4cf72f705512fdf3eda99ca70af9f4800";
    let bridge;
    let validator;
    let asset;

    before('Deploy contracts', async () => {
        validator = await IBCF_Validator.new(primary, 1, chain_id, { from: primary });
        asset = await ERC20.new("TOKEN", "ABC", primary, { from: primary });
        bridge = await IBCF_Bridge.new(validator.address, asset.address, tezos_teleport, { from: primary });

        // Fund accounts
        await asset.mint(primary, "10", { from: primary });

        // Add signers
        await validator.add_signers([signer_address], [public_key], { from: primary });
    })


    it('Call teleport', async function() {
        await expectsFailure(async () => await bridge.teleport(tezos_address, 10, { from: primary }), "Expected error (user must set the allowance).");

        await asset.increaseAllowance(bridge.address, 10, { from: primary });
        await bridge.teleport(tezos_address, 10, { from: primary });
    });

    it('Call receive_teleport', async function() {
        const level = 1;
        const valid_merkle_root = "0x8c5729c8e8e6d3c6d22da098262439b0645c74cef9f5f37ac4f6b4e20d6ddf9a";
        const signature = signContent(pemFormattedKeyPair, buildBuffer(chain_id, level, valid_merkle_root));
        const target_address = "0x1111111111111111111111111111111111111111";

        const signatures = [
            signature
        ];

        const proof = [
            ["0x0000000000000000000000000000000000000000000000000000000000000000", "0xd9b59df48583ee2e099b03cd95c8deb6a07edc3cfaf3288690d1437f71246016"],
            ["0x05fe8371deacdc27859b4c5c1a0c98510d2267d68300fea75d41c383648f0366", "0x0000000000000000000000000000000000000000000000000000000000000000"]
        ];

        const key = "0x11111111111111111111111111111111111111118101";
        const value = "0xd9941111111111111111111111111111111111111111810a8101";

        let account_nonce = await bridge.nonce_of(target_address);
        assert(account_nonce == 0);

        let account_balance = await asset.balanceOf(target_address);
        assert(account_balance == 0);

        await bridge.receive_teleport(level, valid_merkle_root, key, value, proof, [signer_address], signatures);

        account_nonce = await bridge.nonce_of("0x1111111111111111111111111111111111111111");
        assert(account_nonce == 1);

        account_balance = await asset.balanceOf(target_address);
        assert(account_balance == 10);

        // Cannot teleport the same proof twice
        await expectsFailure(async () => await bridge.receive_teleport(level, valid_merkle_root, key, value, proof, [signer_address], signatures), "Expected error (invalid nonce).");
    });
})
