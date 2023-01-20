const { expectsFailure } = require("./utils");

const IBCF_Validator = artifacts.require("IBCF_Validator");

const chain_id = "0xaf1864d9";

contract("IBCF_Validator", async ([alice, primary]) => {
  const state_root_1 =
    "0xfd5f82b627a0b2c5ac0022a95422d435b204c4c1071d5dbda84ae8708d0110fd";

  let instance;
  beforeEach("deploy proof validator", async () => {
    instance = await IBCF_Validator.new(
      primary,
      2,
      chain_id,
      5,
      [alice, primary],
      { from: primary }
    );
  });

  it("Test `submit_state_root` function", async function () {
    const state_root_2 = "0x" + "2".repeat(64);

    await expectsFailure(
      async () =>
        await instance.submit_state_root(2, state_root_1, { from: primary }),
      "Snapshots must be sequential"
    );

    await instance.submit_state_root(1, state_root_1, { from: primary });
    await instance.submit_state_root(1, state_root_1, { from: alice });

    await instance.submit_state_root(2, state_root_2, { from: primary });
  });

  it("Test `get_state_root` view", async function () {
    const state_root_2 = "0x" + "2".repeat(64);
    const state_root_3 = "0x" + "3".repeat(64);

    await instance.submit_state_root(1, state_root_2, { from: primary });
    await instance.submit_state_root(1, state_root_3, { from: primary });
    await instance.submit_state_root(1, state_root_1, { from: primary });
    await expectsFailure(
      async () => await instance.get_state_root.call(1),
      "State root should not have enough endorsements"
    );

    await instance.submit_state_root(1, state_root_1, { from: alice });
    const state_root = await instance.get_state_root.call(1);
    assert(state_root == state_root_1);
  });

  it("Call verify_proof (Valid proof)", async function () {
    const snapshot = 1;

    await instance.submit_state_root(snapshot, state_root_1, { from: primary });
    await instance.submit_state_root(snapshot, state_root_1, { from: alice });

    const proof = [
      [
        "0x19520b9dd118ede4c96c2f12718d43e22e9c0412b39cd15a36b40bce2121ddff",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
      [
        "0x29ac39fe8a6f05c0296b2f57769dae6a261e75a668c5b75bb96f43426e738a7d",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x7e6f448ed8ceff132d032cc923dcd3f49fa7e702316a3db73e09b1ba2beea812",
      ],
      [
        "0x47811eb10e0e7310f8e6c47b736de67b9b68f018d9dc7a224a5965a7fe90d405",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x7646d25d9a992b6ebb996c2c4e5530ffc18f350747c12683ce90a1535305859c",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0xfe9181cc5392bc544a245964b1d39301c9ebd75c2128765710888ba4de9e61ea",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x12f6db53d79912f90fd2a58ec4c30ebd078c490a6c5bd68c32087a3439ba111a",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0xefac0c32a7c7ab5ee5140850b5d7cbd6ebfaa406964a7e1c10239ccb816ea75e",
      ],
      [
        "0xceceb700876e9abc4848969882032d426e67b103dc96f55eeab84f773a7eeb5c",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
      [
        "0xabce2c418c92ca64a98baf9b20a3fcf7b5e9441e1166feedf4533b57c4bfa6a4",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
    ];

    const owner = "0x050a0000001600009f7f36d0241d3e6a82254216d7de5780aa67d8f9";
    const key = "0x0000000000000000000000000003e7";
    const value = "0x0000000000000000000000000003e7";
    await instance.verify_proof.call(snapshot, owner, key, value, proof);
    console.log(
      "\n\tConsumed gas: ",
      await instance.verify_proof.estimateGas(
        snapshot,
        owner,
        key,
        value,
        proof
      )
    );
  });

  it("Call verify_proof 2 (Valid proof)", async function () {
    const snapshot = 1;
    const state_root =
      "0xe454c3e9cc4e8d3297a9770a60791ca4e7083b12f59ef082ad91768c825fc2c3";

    await instance.submit_state_root(snapshot, state_root, { from: primary });
    await instance.submit_state_root(snapshot, state_root, { from: alice });

    const proof = [
      [
        "0x77e9d904a5433b61e7b2eb1f0f271cc24492acb00f8c19a642a27f7c126ddfa1",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0xc332e8089ae5a06975fafe0a4d4c495679e1f1fb4089e2257f7a59bcaca2ffaa",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0xcdbacddfed638c93aaa8c21658fcfa67823c997174ee6110212c2a0f8d0b589c",
      ],
    ];

    const owner = "0x050a0000001600008a8584be3718453e78923713a6966202b05f99c6";
    const key = "0x05";
    const value = "0xffffffffff";
    await instance.verify_proof.call(snapshot, owner, key, value, proof);
    console.log(
      "\n\tConsumed gas: ",
      await instance.verify_proof.estimateGas(
        snapshot,
        owner,
        key,
        value,
        proof
      )
    );
  });

  it("Call verify_proof (Invalid signature)", async function () {
    const snapshot = 1;

    await instance.submit_state_root(snapshot, state_root_1, { from: primary });
    await instance.submit_state_root(snapshot, state_root_1, { from: alice });

    const proof = [
      [
        "0x19520b9dd118ede4c96c2f12718d43e22e9c0412b39cd15a36b40bce2121ddff",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
      [
        "0x29ac39fe8a6f05c0296b2f57769dae6a261e75a668c5b75bb96f43426e738a7d",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x7e6f448ed8ceff132d032cc923dcd3f49fa7e702316a3db73e09b1ba2beea812",
      ],
      [
        "0x47811eb10e0e7310f8e6c47b736de67b9b68f018d9dc7a224a5965a7fe90d405",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x7646d25d9a992b6ebb996c2c4e5530ffc18f350747c12683ce90a1535305859c",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0xfe9181cc5392bc544a245964b1d39301c9ebd75c2128765710888ba4de9e61ea",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x12f6db53d79912f90fd2a58ec4c30ebd078c490a6c5bd68c32087a3439ba111a",
      ],
      [
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0xefac0c32a7c7ab5ee5140850b5d7cbd6ebfaa406964a7e1c10239ccb816ea75e",
      ],
      [
        "0xceceb700876e9abc4848969882032d426e67b103dc96f55eeab84f773a7eeb5c",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
      ],
    ];

    const owner = "0x050a0000001600009f7f36d0241d3e6a82254216d7de5780aa67d8f9";
    const key = "0x0000000000000000000000000003e7";
    const value = "0x0000000000000000000000000003e7";
    await expectsFailure(
      async () =>
        await instance.verify_proof.call(snapshot, owner, key, value, proof),
      "Signature expected to be invalid."
    );
  });
});
