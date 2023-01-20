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
          items: ["developers/examples/generating-proofs"],
          collapsed: false,
        }
      ],
      collapsed: false,
    },
    {
      type: "category",
      label: "State Relaying",
      items: [
        "relay-contracts/overview",
        {
          type: "category",
          label: "Tezos Contracts",
          items: ["relay-contracts/tezos/state", "relay-contracts/tezos/validator"],
          collapsed: false,
        },
        {
          type: "category",
          label: "EVM Contracts",
          items: ["relay-contracts/evm/validator"],
          collapsed: false,
        }
      ],
      collapsed: false,
    },
    "deployments"
  ],
};

module.exports = sidebars;
