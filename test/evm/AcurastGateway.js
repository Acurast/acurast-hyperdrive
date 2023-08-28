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
            // allow_only_verified_sources: true,
            destination: "0x918eFEF09c0Ef0fDF488f1306466cEDD9E741b6b",
            requirements: {
                slots: 2,
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
        // function a(o) {
        //     return Object.values(o).map(v => typeof(v) == "object" ? a(v) : v);
        // }
        //console.log(JSON.stringify(a(arg)))
        //console.log(await this.acurastGatewayV2.register_job(arg))
        await this.acurastGatewayV2.register_job(arg, {from: primary, value: 200 });
    });

    it('Receive noop message', async function () {
        const snapshot = 1;
        const mmr_size = 3;
        const root = "0xf805950edaf6f0ee75cf7ba469c2ea381667f1b75d5bfacf1749500448019049";
        const proof_items = ["0x79dd2180cc76e44fd7d3b6d1c89b9dfae07800741f7d36837d64bedd7300ed2e"];
        const leaves = [
            {
                k_index: 1,
                leaf_index: 1,
                data: "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000ff000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000"
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

    it('Receive assign_job_processor message', async function () {
        const snapshot = 1;
        const mmr_size = 3;
        const root = "0x4a1b0f75b84c5889aabb63aa60e239dd31a6984a7859669e728f701143e088b6";
        const proof_items = ["0x7f2b55cdca847a711b533639374ffbc98e176c9360af938b70fa72a198ca8c5a"];
        const leaves = [
            {
                k_index: 1,
                leaf_index: 1,
                data: "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000001000000000000000000000000d91e25b70ca8d302d242ba96dc032673cfbc66c9"
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
