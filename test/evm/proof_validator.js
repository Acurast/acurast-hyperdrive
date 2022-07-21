const assert = require("assert");
const crypto         = require('crypto');
const ecPem          = require('ec-pem');
const ethereumJSUtil = require('ethereumjs-util');

const IBCF_Validator = artifacts.require('IBCF_Validator')

async function expectsFailure(call, msg) {
    try {
        await call()
    } catch {
        return true;
    }

    throw new Error(msg || "Expected to fail, but passed.")
}

contract('IBCF_Validator', async ([_, primary]) => {
    const valid_merkle_root = "0xfd5f82b627a0b2c5ac0022a95422d435b204c4c1071d5dbda84ae8708d0110fd";

    let pemFormattedKeyPair;
    let instance;
    beforeEach('deploy proof validator', async () => {
        // Create curve object for key and signature generation.
        const prime256v1 = crypto.createECDH('prime256v1');
        prime256v1.generateKeys();

        // Reformat keys.
        pemFormattedKeyPair = ecPem(prime256v1, 'prime256v1');
        const public_key = [
            '0x' + prime256v1.getPublicKey('hex').slice(2, 66),
            '0x' + prime256v1.getPublicKey('hex').slice(-64)
        ];
        instance = await IBCF_Validator.new(primary, public_key, { from: primary })
    })

    it('Call submit_merkle_root_restricted (Valid)', async function() {
        await instance.submit_merkle_root_restricted(1, valid_merkle_root, {from: primary});
    })

    it('Call submit_merkle_root_restricted (Invalid)', async function() {
        await expectsFailure(async () => await instance.submit_merkle_root_restricted(1, valid_merkle_root));
    })

    it('Call add_merkle_root (Invalid signature)', async function() {
        v= 27
        r="0x39115c1cf79bebc100767dd50f72132de818b9b55d40a65680a552eedc67195c"
        s="0x2c43510fb0c90edd5b2e1159edbf7f4940fff53094afb45e70c8b773e38a078e"

        await expectsFailure(async () => await instance.add_merkle_root(1, valid_merkle_root, v, r, s));
    })

    it('Call add_merkle_root (Valid signature)', async function() {
        const admin_address = "0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0";
        await instance.update_administrator(admin_address, {from: primary});

        v= 27
        r="0x39115c1cf79bebc100767dd50f72132de818b9b55d40a65680a552eedc67195c"
        s="0x2c43510fb0c90edd5b2e1159edbf7f4940fff53094afb45e70c8b773e38a078e"
        await instance.add_merkle_root(1, valid_merkle_root, v, r, s)
    })

    it('Call verify_proof (Valid proof)', async function() {
        const level = 867292;
        await instance.submit_merkle_root_restricted(level, valid_merkle_root, {from: primary})

        const proof = [
            ['0x19520b9dd118ede4c96c2f12718d43e22e9c0412b39cd15a36b40bce2121ddff', '0x0000000000000000000000000000000000000000000000000000000000000000'],
            ['0x29ac39fe8a6f05c0296b2f57769dae6a261e75a668c5b75bb96f43426e738a7d', '0x0000000000000000000000000000000000000000000000000000000000000000'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0x7e6f448ed8ceff132d032cc923dcd3f49fa7e702316a3db73e09b1ba2beea812'],
            ['0x47811eb10e0e7310f8e6c47b736de67b9b68f018d9dc7a224a5965a7fe90d405', '0x0000000000000000000000000000000000000000000000000000000000000000'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0x7646d25d9a992b6ebb996c2c4e5530ffc18f350747c12683ce90a1535305859c'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0xfe9181cc5392bc544a245964b1d39301c9ebd75c2128765710888ba4de9e61ea'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0x12f6db53d79912f90fd2a58ec4c30ebd078c490a6c5bd68c32087a3439ba111a'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0xefac0c32a7c7ab5ee5140850b5d7cbd6ebfaa406964a7e1c10239ccb816ea75e'],
            ['0xceceb700876e9abc4848969882032d426e67b103dc96f55eeab84f773a7eeb5c', '0x0000000000000000000000000000000000000000000000000000000000000000'],
            ['0xabce2c418c92ca64a98baf9b20a3fcf7b5e9441e1166feedf4533b57c4bfa6a4', '0x0000000000000000000000000000000000000000000000000000000000000000']
        ]

        const owner = "0x050a0000001600009f7f36d0241d3e6a82254216d7de5780aa67d8f9";
        const key = "0x0000000000000000000000000003e7";
        const value = "0x0000000000000000000000000003e7";
        await instance.verify_proof.call(level, owner, key, value, proof);
        console.log("\n\tConsumed gas: ", await instance.verify_proof.estimateGas(level, owner, key, value, proof))
    })

    it('Call verify_proof (Invalid proof)', async function() {
        const level = 867292;
        await instance.submit_merkle_root_restricted(level, valid_merkle_root, {from: primary})

        const proof = [
            ['0x19520b9dd118ede4c96c2f22718d43e22e9c0412b39cd15a36b40bce2121ddff', '0x0000000000000000000000000000000000000000000000000000000000000000'],
            ['0x29ac39fe8a6f05c0296b2f57769dae6a261e75a668c5b75bb96f43426e738a7d', '0x0000000000000000000000000000000000000000000000000000000000000000'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0x7e6f448ed8ceff132d032cc923dcd3f49fa7e702316a3db73e09b1ba2beea812'],
            ['0x47811eb10e0e7310f8e6c47b736de67b9b68f018d9dc7a224a5965a7fe90d405', '0x0000000000000000000000000000000000000000000000000000000000000000'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0x7646d25d9a992b6ebb996c2c4e5530ffc18f350747c12683ce90a1535305859c'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0xfe9181cc5392bc544a245964b1d39301c9ebd75c2128765710888ba4de9e61ea'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0x12f6db53d79912f90fd2a58ec4c30ebd078c490a6c5bd68c32087a3439ba111a'],
            ['0x0000000000000000000000000000000000000000000000000000000000000000', '0xefac0c32a7c7ab5ee5140850b5d7cbd6ebfaa406964a7e1c10239ccb816ea75e'],
            ['0xceceb700876e9abc4848969882032d426e67b103dc96f55eeab84f773a7eeb5c', '0x0000000000000000000000000000000000000000000000000000000000000000'],
            ['0xabce2c418c92ca64a98baf9b20a3fcf7b5e9441e1166feedf4533b57c4bfa6a4', '0x0000000000000000000000000000000000000000000000000000000000000000']
        ]

        const owner = "0x050a0000001600009f7f36d0241d3e6a82254216d7de5780aa67d8f9";
        const key = "0x0000000000000000000000000003e7";
        const value = "0x0000000000000000000000000003e7";
        await expectsFailure(async () => await instance.verify_proof.call(level, owner, key, value, proof), "The merkle root does not match");
    })

    it('Verify secp256r1 signature (Valid)', async function() {
        // Hex32Bytes(level = 1) + valid_merkle_root
        const content = Buffer.from("0000000000000000000000000000000000000000000000000000000000000001fd5f82b627a0b2c5ac0022a95422d435b204c4c1071d5dbda84ae8708d0110fd", "hex");

        // Create signature.
        const signer = crypto.createSign('RSA-SHA256');
        signer.update(content);
        let sigString = signer.sign(pemFormattedKeyPair.encodePrivateKey(), 'hex');

        // Reformat signature / extract coordinates.
        const xlength = 2 * ('0x' + sigString.slice(6, 8));
        sigString = sigString.slice(8)
        const signature = [
            '0x' + sigString.slice(0, xlength),
            '0x' + sigString.slice(xlength + 4)
        ];

        let estimatedGasToAddNewValue = await instance.submit_merkle_root.estimateGas(1, valid_merkle_root, signature)
        assert(await instance.submit_merkle_root.call(1, valid_merkle_root, signature), "Signature expected to be valid.")
        console.log("\n\tConsumed gas: ", estimatedGasToAddNewValue)
    })

    it('Verify secp256r1 signature (Invalid)', async function() {
        const signature = [
            "0x7d5d392b8f88052321a2d90ae0834f78eabe04c746db08def160fe53add526ae",
            "0x00e9c63d65b43492b646d94bc0cf8cc90e4f8b1eb92a06a90534ccf02d9d2d2b1b"
        ];

        await expectsFailure(async () => await instance.submit_merkle_root.call(1, valid_merkle_root, signature), "Signature expected to be invalid.");
    })
})
