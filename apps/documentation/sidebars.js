/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docs: [
    "introduction",
    {
      type: "category",
      label: "Developers",
      items: [
        "developers/get-started",
        {
          type: "category",
          label: "Examples",
          items: [
            "developers/examples/generating-proofs",
            {
              type: "category",
              label: "Application Blueprints",
              items: ["developers/examples/blueprints/crowdfund", "developers/examples/blueprints/bridge"],
              collapsed: false,
            }
          ],
          collapsed: false,
        },
        "developers/toolkits",
      ],
      collapsed: false,
    },
    {
      type: "category",
      label: "Cross-chain state sharing",
      items: [
        "relay-contracts/overview",
        {
          type: "category",
          label: "Tezos Contracts",
          items: [
            "relay-contracts/tezos/state",
            "relay-contracts/tezos/validator",
          ],
        },
        {
          type: "category",
          label: "EVM Contracts",
          items: ["relay-contracts/evm/validator"],
        },
      ],
    },
    "deployments",
  ],
};

module.exports = sidebars;
