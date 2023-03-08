/**
 * Use this file to configure your truffle project. It's seeded with some
 * common settings for different networks and features like migrations,
 * compilation, and testing. Uncomment the ones you need or modify
 * them to suit your project as necessary.
 *
 * More information about configuration can be found at:
 *
 * https://trufflesuite.com/docs/truffle/reference/configuration
 *
 * To deploy via Infura you'll need a wallet provider (like @truffle/hdwallet-provider)
 * to sign your transactions before they're sent to a remote public node. Infura accounts
 * are available for free at: infura.io/register.
 *
 * You'll also need a mnemonic - the twelve word phrase the wallet uses to generate
 * public/private key pairs. If you're publishing your code to GitHub make sure you load this
 * phrase from a file you've .gitignored so it doesn't accidentally become public.
 *
 */

const HDWalletProvider = require("@truffle/hdwallet-provider");
module.exports = {
  contracts_build_directory: "__SNAPSHOTS__/compilation/evm",
  migrations_directory: "deployment/evm",
  networks: {
    goerli: {
      provider: () =>
        new HDWalletProvider({
          privateKeys: [process.env["PRIVATE_KEY"]],
          providerOrUrl: process.env["RPC_URL"],
        }),
      network_id: 5, // goerli's id
      gas: 4465030,
      confirmations: 2, // # of confirmations to wait between deployments. (default: 0)
      timeoutBlocks: 200, // # of blocks before a deployment times out  (minimum/default: 50)
      skipDryRun: true, // Skip dry run before migrations? (default: false for public nets )
    },
    mumbai: {
      provider: () =>
        new HDWalletProvider({
          privateKeys: [process.env["PRIVATE_KEY"]],
          providerOrUrl: process.env["RPC_URL"],
        }),
      network_id: 80001,
      gas: 4465030,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true,
    },
    bsc: {
      provider: () =>
        new HDWalletProvider({
          privateKeys: [process.env["PRIVATE_KEY"]],
          providerOrUrl: process.env["RPC_URL"],
        }),
      network_id: 97,
      gas: 4465030,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true,
    },
    avalanche: {
      provider: () =>
        new HDWalletProvider({
          privateKeys: [process.env["PRIVATE_KEY"]],
          providerOrUrl: process.env["RPC_URL"],
        }),
      network_id: 0xa869,
      gas: 4465030,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true,
    },
  },

  // Set default mocha options here, use special reporters, etc.
  mocha: {
    timeout: 100000,
  },

  // Configure your compilers
  compilers: {
    solc: {
      version: "0.8.17", // Fetch exact version from solc-bin (default: truffle's version)
      // docker: true,        // Use "0.5.1" you've installed locally with docker (default: false)
      // settings: {          // See the solidity docs for advice about optimization and evmVersion
      //  optimizer: {
      //    enabled: false,
      //    runs: 200
      //  },
      //  evmVersion: "byzantium"
      // }
    },
  },
};
