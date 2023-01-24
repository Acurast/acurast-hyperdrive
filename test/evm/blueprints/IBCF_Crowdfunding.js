const IBCF_Crowdfunding = artifacts.require("IBCF_Crowdfunding");

contract("IBCF_Crowdfunding", async ([_, primary]) => {
  let crowdfunding;

  before("Deploy contract", async () => {
    crowdfunding = await IBCF_Crowdfunding.new({from: primary});
  });

  it("Participate", async function () {
    const tx = await crowdfunding.send(1, { from: primary });

    assert(tx.logs[0].event == "Funding");
    assert(tx.logs[0].args.funder == primary);
    assert(tx.logs[0].args.amount == 1);
    assert(tx.logs[0].args.nonce == 1);
  });
});
