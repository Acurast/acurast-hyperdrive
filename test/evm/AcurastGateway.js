const Web3 = require("web3");
const { deployProxy, upgradeProxy } = require('@openzeppelin/truffle-upgrades');

const MMR_Validator = artifacts.require("MMR_Validator");
const AcurastGateway = artifacts.require("AcurastGateway");
const AcurastGatewayV2 = artifacts.require("AcurastGatewayV2");


contract('AcurastGateway (proxy)', function ([alice, primary]) {
    beforeEach(async function () {
        this.mmr_validator = await MMR_Validator.new(
            primary,
            2,
            5,
            [alice, primary],
            { from: primary }
          );
        this.acurastGateway = await deployProxy(AcurastGateway, [this.mmr_validator.address], {initializer: 'initialize'});
        this.acurastGatewayV2 = await upgradeProxy(this.acurastGateway.address, AcurastGatewayV2);
    });

    // Test case
    it('retrieve returns a value previously initialized', async function () {
        const arg = {
            allowedSources: [],
            allowOnlyVerifiedSources: true,
            destination: "0x918eFEF09c0Ef0fDF488f1306466cEDD9E741b6b",
            requirements: {
                slots: 0,
                reward: 0,
                minReputation: 0,
                instantMatch: []
            },
            expectedFulfillmentFee: 0,
            requiredModules: [],
            script: "0x00",
            schedule: {
                duration: 0,
                startTime: 0,
                endTime: 0,
                interval: 0,
                maxStartDelay: 0,
            },
            memoryCapacity: 0,
            networkRequests: 0,
            storageCapacity: 0,
        };
        function a(o) {
            return Object.values(o).map(v => typeof(v) == "object" ? a(v) : v);
        }
        //console.log(JSON.stringify(a(arg)))
        //console.log(await this.acurastGatewayV2.register_job(arg))
        await this.acurastGatewayV2.register_job(arg);
    });

    it('Receive noop message', async function () {
        const snapshot = 1;
        const mmr_size = 3;
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

        await this.mmr_validator.submit_state_root(snapshot, root, { from: primary });
        await this.mmr_validator.submit_state_root(snapshot, root, { from: alice });

        const proof = {
            snapshot,
            mmr_size,
            leaves,
            proof: proof_items,
        }
        await this.acurastGatewayV2.receive_messages(proof)
    });
});
