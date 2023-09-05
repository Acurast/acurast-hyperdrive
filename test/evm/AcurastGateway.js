const Web3 = require("web3");
const { deployProxy, upgradeProxy } = require('@openzeppelin/truffle-upgrades');

const MMR_Validator = artifacts.require("MMR_Validator");
const AcurastAsset = artifacts.require("Asset");
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
        this.acurastGateway = await deployProxy(AcurastGateway, [this.mmr_validator.address, primary], {initializer: 'initialize'});
        this.acurastGatewayV2 = await upgradeProxy(this.acurastGateway.address, AcurastGatewayV2);

        this.acurast_asset = await AcurastAsset.new("Acurast Canary Asset", "ACU", primary);
        await this.acurast_asset.mint(primary, 1000000, {from: primary});
        await this.acurast_asset.set_manager(this.acurastGatewayV2.address, {from: primary});
        await this.acurastGatewayV2.set_asset(this.acurast_asset.address, {from: primary});
    });

    // Test case
    it('Register a job', async function () {
        const arg = {
            allowed_sources: [],
            allow_only_verified_sources: true,
            destination: "0x918eFEF09c0Ef0fDF488f1306466cEDD9E741b6b",
            requirements: {
                slots: 1,
                reward: 11,
                min_reputation: 100,
                instant_match: []
            },
            expected_fullfilment_fee: 100,
            required_modules: [],
            script: "0x00",
            schedule: {
                duration: 10,
                start_time: 10,
                end_time: 20,
                interval: 10,
                max_start_delay: 10,
            },
            memory_capacity: 10,
            network_requests: 10,
            storage_capacity: 10,
        };

        await this.acurastGatewayV2.faucet(1000000000);

        function a(o) {
            return Object.values(o).map(v => typeof(v) == "object" ? a(v) : v);
        }
        console.log(JSON.stringify(a(arg)))
        await this.acurastGatewayV2.register_job(arg, {from: primary, value: 100 });
    });

    it('Receive multi noop messages', async function () {
        const snapshot_1 = 1;
        const mmr_size = 8;
        const root = "0xe441d51617e81fa05e565f597445e342033ac58e77212fd0c2cb71c385940ab8";
        const proof_items = [];
        const leaves = [
            {
                k_index: 0,
                leaf_index: 0,
                data: "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000ff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000"
            },
            {
                k_index: 1,
                leaf_index: 1,
                data: "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000ff000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000"
            },
            {
                k_index: 2,
                leaf_index: 3,
                data: "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000ff000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000"
            },
            {
                k_index: 3,
                leaf_index: 4,
                data: "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000ff000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000"
            },
            {
                k_index: 0,
                leaf_index: 7,
                data: "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000ff000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000"
            }
        ];

        await this.mmr_validator.submit_state_root(snapshot_1, root, { from: primary });
        await this.mmr_validator.submit_state_root(snapshot_1, root, { from: alice });

        const proof_1 = {
            snapshot: snapshot_1,
            mmr_size,
            leaves,
            proof: proof_items,
        }

        await this.acurastGatewayV2.receive_messages(proof_1)

        assert(await this.acurastGatewayV2.in_seq_id() == 5)
    });
});
