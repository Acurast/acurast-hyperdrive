# Inter Blockchain Communication Framework

IBCF is a building block allowing for general bidirectional message passing between Tezos and Ethereum networks.

It allows smart contracts on a source chain to store ✉️ states that are verifiable on a target chain. It provides a generic way for contracts to communicate between chains by means of validating Merkle proofs about these states stored in the source chain.

# [Protocol documentation](https://airgap-it.github.io/ibcf)

## Dependencies

|                                                   |
| ------------------------------------------------- |
| [GNU Make 4.3](https://www.gnu.org/software/make) |
| [Python 3](https://www.python.org)                |
| [Curl](https://curl.se)                           |
| [npm](https://github.com/npm/cli)                 |
| [yarn](https://yarnpkg.com/)                      |
| [nodejs](https://nodejs.org/en)                   |

## Contract Compilation

```sh
# Compile all contracts
make compile

# Compile only tezos contracts
make compile-tezos

# Compile only evm contracts
make compile-evm

# Run a single compilation (tezos only)
make compilations/<compilation_file_without_extension>
```

## Contract Testing

### Unit tests

```sh
# Test all contracts
make test

# Test only tezos contracts
make test-tezos

# Test only evm contracts
make test-evm

# Run a single test (tezos only)
make tests/<test_file_without_extension>
```

## Deployment

The Tezos deployment outputs the results to `stdout` and creates a snapshot file at `__SNAPSHOTS__/deployment-*.yaml`.

The Ethereum deployment outputs the results to `stdout` and creates a snapshot file at `__SNAPSHOTS__/evm-deployment.txt`.

```sh
# Tezos deployment (CONFIG_PATH environment variable is optional)
CONFIG_PATH=deployment/configs/ghostnet.yaml make deploy-tezos

# Evm deployment (ETH_PRIVATE_KEY and INFURA_URL environment variables are not optional)
PRIVATE_KEY=<private_key> INFURA_URL=https://<network>.infura.io/v3/<project_api_key> make deploy-evm
```

#### Tezos deployment configuration

New deployment configurations can be added by creating a [<config_name>.yaml](https://yaml.org/spec/1.2.2) file in [configs](./deployment/tezos/configs) folder.

Have a look at the [deployment/tezos/configs/ghostnet.yaml](./deployment/configs/ghostnet.yaml) configuration file.

#### Ethereum deployment configuration

Have a look at [deployment/evm/0_all.js](./deployment/evm/0_all.js) file.

## Flextesa sandbox

The sandbox is used to test the contract deployments locally. It is configured to produce `1` block every second.

|         |                          |
| ------- | ------------------------ |
| RPC URL | `http://localhost:20000` |

`Default accounts:`

```
- alice
  * edpkvGfYw3LyB1UcCahKQk4rF2tvbMUk8GFiTuMjL75uGXrpvKXhjn
  * tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
  * unencrypted:edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq
  * balance: 2000000 ꜩ
- bob
  * edpkurPsQ8eUApnLUJ9ZPDvu98E8VNj4KtJa1aZr16Cr5ow5VHKnz4
  * tz1aSkwEot3L2kmUvcoxzjMomb9mvBNuzFK6
  * unencrypted:edsk3RFfvaFaxbHx8BMtEW1rKQcPtDML3LXjNqMNLCzC3wLC1bWbAt
  * balance: 2000000 ꜩ
```

```sh
# Start the sandbox
make start-sandbox

# Stop the sanbox
make stop-sandbox
```

## Code formatter

```sh
# Run a code format check
make fmt-check

# Format code
make fmt-fix
```

## Demo application

- [Bridge](./apps/bridge-playground)

## Packages

- [SDK](./packages/ibcf-sdk)
