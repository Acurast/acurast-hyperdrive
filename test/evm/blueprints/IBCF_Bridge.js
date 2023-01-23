const { expectsFailure } = require("../utils");

const IBCF_Bridge = artifacts.require("IBCF_Bridge");
const IBCF_Validator = artifacts.require("IBCF_Validator");
const ERC20 = artifacts.require("MintableERC20");

contract("IBCF_Bridge", async ([_, primary]) => {
  const chain_id = "0xaf1864d9";
  const tezos_bridge =
    "0x050a0000001601d1371b91c7491542e97deee96091e28a80b2335900";
  const tezos_address =
    "0x050a0000001601d1371b91c7491542e97deee96091e28a80b2335900";
  let bridge;
  let validator;
  let asset;

  before("Deploy contracts", async () => {
    validator = await IBCF_Validator.new(primary, 1, chain_id, 5, [primary], {
      from: primary,
    });
    asset = await ERC20.new("TOKEN", "ABC", { from: primary });
    bridge = await IBCF_Bridge.new(validator.address, asset.address, {
      from: primary,
    });

    // Fund accounts
    await asset.mint(primary, "10", { from: primary });
  });

  it("Call set_tezos_bridge_address", async function () {
    await bridge.set_tezos_bridge_address(tezos_bridge, { from: primary });

    await expectsFailure(
      async () =>
        await bridge.set_tezos_bridge_address(tezos_bridge, { from: primary }),
      "Expected error (user must set the allowance)."
    );
  });

  it("Call wrap", async function () {
    await expectsFailure(
      async () => await bridge.wrap(tezos_address, 10, { from: primary }),
      "Expected error (user must set the allowance)."
    );

    await asset.approve(bridge.address, 10, { from: primary });
    await bridge.wrap(tezos_address, 10, { from: primary });
  });

  it("Call unwrap", async function () {
    const snapshot = 1;
    const valid_merkle_root =
      "0x9d14356ed03a5da92aaad50a7b838ee4bb41baaa0746edadb21bbfbe4cd018d5";
    const target_address = "0x1111111111111111111111111111111111111111";

    await validator.submit_state_root(snapshot, valid_merkle_root, {
      from: primary,
    });

    let account_balance = await asset.balanceOf(target_address);
    assert(account_balance.toNumber() == 0);

    const proof = [
      [
        "0x38517ca2532ce3b5d665a30581e983f8d9967c19e98f5443922114198b9c35d3",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
    ];

    const key = "0x8101";
    const value = "0xd79411111111111111111111111111111111111111118109";

    await bridge.unwrap(snapshot, key, value, proof);

    account_balance = await asset.balanceOf(target_address);
    assert(account_balance.toNumber() == 9);

    // Cannot teleport the same proof twice
    await expectsFailure(
      async () => await bridge.unwrap(snapshot, key, value, proof),
      "Expected error (invalid nonce)."
    );
  });
});
