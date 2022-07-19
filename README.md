# Inter Blockchain Communication Framework

![image](merkle_tree.png)

## Dependencies

| |
|-|
| [GNU Make 4.3](https://www.gnu.org/software/make) |
| [Python 3](https://www.python.org) |
| [Curl](https://curl.se) |
| [npm](https://github.com/npm/cli) |
| [nodejs](https://nodejs.org/en) |

## Contract Compilation

```sh
# Compile all contracts
make compile

# Run a single compilation
make compilations/<compilation_file_without_extension>
```

## Contract Testing

### Unit tests

```sh
# Test all contracts
make test

# Run a single test
make tests/<test_file_without_extension>
```

## Deployment

The deployment target outputs the results to `stdout` and creates a snapshot file at `__SNAPSHOTS__/deployment-*.yaml`.

```sh
CONFIG_PATH=deployment/configs/ghostnet.yaml make deploy
```

#### Configuration

New deployment configurations can be added by creating a [<config_name>.yaml](https://yaml.org/spec/1.2.2) file in [configs](./deployment/configs) folder.

Have a look at the [deployment/configs/ghostnet.yaml](./deployment/configs/ghostnet.yaml) configuration file.

## Flextesa sandbox

The sandbox is used to test the contract deployments locally. It is configured to produce `1` block every second.

| | |
|--|--|
|RPC URL| `http://localhost:20000` |

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

## Scripts

### Get proof

```sh
python scripts/extract_proof.py https://tezos-ithacanet-node-1.diamond.papers.tech KT19NH1awRGaVNkZSwY2c96nChMWdp6SU39F

# {'level': 867292,
#  'merkle_root': '0xfd5f82b627a0b2c5ac0022a95422d435b204c4c1071d5dbda84ae8708d0110fd',
#  'proof': [['0x19520b9dd118ede4c96c2f12718d43e22e9c0412b39cd15a36b40bce2121ddff',
#             ''],
#            ['0x29ac39fe8a6f05c0296b2f57769dae6a261e75a668c5b75bb96f43426e738a7d',
#             ''],
#            ['',
#             '0x7e6f448ed8ceff132d032cc923dcd3f49fa7e702316a3db73e09b1ba2beea812'],
#            ['0x47811eb10e0e7310f8e6c47b736de67b9b68f018d9dc7a224a5965a7fe90d405',
#             ''],
#            ['',
#             '0x7646d25d9a992b6ebb996c2c4e5530ffc18f350747c12683ce90a1535305859c'],
#            ['',
#             '0xfe9181cc5392bc544a245964b1d39301c9ebd75c2128765710888ba4de9e61ea'],
#            ['',
#             '0x12f6db53d79912f90fd2a58ec4c30ebd078c490a6c5bd68c32087a3439ba111a'],
#            ['',
#             '0xefac0c32a7c7ab5ee5140850b5d7cbd6ebfaa406964a7e1c10239ccb816ea75e'],
#            ['0xceceb700876e9abc4848969882032d426e67b103dc96f55eeab84f773a7eeb5c',
#             ''],
#            ['0xabce2c418c92ca64a98baf9b20a3fcf7b5e9441e1166feedf4533b57c4bfa6a4',
#             '']]}
```

### Visualize current merkle tree

```sh
# This will create a merkle_tree.png at $PWD
python scripts/visualize_tree.py https://tezos-ithacanet-node-1.diamond.papers.tech KT1VPoRPnHyReNxQF3KzgUXyNcDy2EVJ2PU8
```
