const Web3 = require("web3");

const MerkleMountainRange = artifacts.require("MerkleMountainRange");


contract('Merkle mountain range', function () {
    let instance;
    beforeEach(async function () {
        instance = await MerkleMountainRange.new();
    });

    it('Validate noop proof', async function () {
        const root = "0x57f88dbc0f80032c952638b253c750b1b47e5247ab2a9b2092a7ede81c1bafa7";
        const proof_items = ["0x1e98d6cc38508d55ed3a243dd1bdbfec3ad6d2c63e0c1c709f03586daf36d00b"];
        const leaves = [
            {
                k_index: 1,
                leaf_index: 1,
                hash: Web3.utils.sha3(
                    "0x00000000000000000000000000000000000000000000000000000000000000ff0000000000000000000000000000000000000000000000000000000000000001c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
                ),
            }
        ];
        const mmrSize = 3;
        assert(await instance.CalculateRoot(proof_items, leaves, mmrSize) == root)
    });
});
