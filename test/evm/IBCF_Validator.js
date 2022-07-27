const { signContent, buildBuffer, expectsFailure, createSecp256r1KeyPair} = require("./utils");

const IBCF_Validator = artifacts.require('IBCF_Validator')

let [public_key, pemFormattedKeyPair] = createSecp256r1KeyPair();

contract('IBCF_Validator', async ([_, primary]) => {
    let instance;
    beforeEach('deploy proof validator', async () => {
        instance = await IBCF_Validator.new(primary, { from: primary })

        // Add signers
        await instance.add_signers([primary], [public_key], { from: primary })
    })

    it('Call verify_proof (Valid proof)', async function() {
        const level = 1;
        const valid_merkle_root = "0xfd5f82b627a0b2c5ac0022a95422d435b204c4c1071d5dbda84ae8708d0110fd";
        const signature = signContent(pemFormattedKeyPair, buildBuffer(level, valid_merkle_root));

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
        await instance.verify_proof.call(level, valid_merkle_root, owner, key, value, proof, [primary], [signature]);
        console.log("\n\tConsumed gas: ", await instance.verify_proof.estimateGas(level, valid_merkle_root, owner, key, value, proof, [primary], [signature]))
    })

    it('Call verify_proof (Invalid signature)', async function() {
        const level = 1;
        const valid_merkle_root = "0xfd5f82b627a0b2c5ac0022a95422d435b204c4c1071d5dbda84ae8708d0110fd";
        const signature = [
            "0x007d5d392b8f88052321a2d90ae0834f78eabe04c746db08def160fe53add526ae",
            "0x00e9c63d65b43492b646d94bc0cf8cc90e4f8b1eb92a06a90534ccf02d9d2d2b1b"
        ];

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
        await expectsFailure(async () => await instance.verify_proof.call(level, valid_merkle_root, owner, key, value, proof, [primary], [signature]), "Signature expected to be invalid.");
    })

    it('Call verify_proof (Invalid proof)', async function() {
        const level = 1;
        const valid_merkle_root = "0xfd5f82b627a0b2c5ac0022a95422d435b204c4c1071d5dbda84ae8708d0110fd";
        const content = buildBuffer(level, valid_merkle_root);
        const signature = signContent(pemFormattedKeyPair, content);
        const proof = [
            ['0x19520b9dd118ede4c96c2f12718d43e22e9c0412b39cd15a36b40bce2121ddff', '0x0000000000000000000000000000000000000000000000000000000000000000'],
        ]

        const owner = "0x050a0000001600009f7f36d0241d3e6a82254216d7de5780aa67d8f9";
        const key = "0x0000000000000000000000000003e7";
        const value = "0x0000000000000000000000000003e7";
        await expectsFailure(async () => await instance.verify_proof.call(level, valid_merkle_root, owner, key, value, proof, [primary], [signature]), "Proof expected to be invalid.");
    })
})
