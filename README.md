# Inter Blockchain Communication Framework

## Dependencies

| |
|-|
| [GNU Make 4.3](https://www.gnu.org/software/make) |
| [Python 3](https://www.python.org) |
| [Curl](https://curl.se) |
| [npm](https://github.com/npm/cli) |

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
