# Inter Blockchain Communication Framework SDK

## Install

```sh
yarn add ibcf-sdk
```

## Usage

### Generate a proof-of-inclusion of a state stored on Tezos

```ts
import { Tezos } from 'ibcf-sdk';
import { TezosToolkit } from '@taquito/taquito';

const TEZOS_RPC = 'https://rpc.ghostnet.teztnets.xyz';
const STATE_AGGREGATOR_CONTRACT = 'KT1Aqdz8opKsfADxmF2vf6NMoYwgamL5R4KT';

const tezosSdk = new TezosToolkit(TEZOS_RPC);
const stateAggregator = new Tezos.Contracts.StateAggregator.Contract(tezosSdk, STATE_AGGREGATOR_CONTRACT);

const STATE_ORIGIN = 'KT1AfcN12T2d43XtJLbahmpDr13xda4Zedxx';
const STATE_KEY = '0x01';
const SNAPSHOT_LEVEL = '1805119';

stateAggregator
    .getProof(
        STATE_ORIGIN, // Origin
        STATE_KEY, // State key
        SNAPSHOT_LEVEL, // Block level where the snapshot was taken
    )
    .then(console.log);
```

### Generate a proof-of-inclusion of a state stored on EVM

```ts
import { Ethereum } from 'ibcf-sdk';
import { ethers } from 'ethers';

const ETHEREUM_RPC = 'https://goerli.infura.io/v3/75829a5785c844bc9c9e6e891130ee6f';
const ETHEREUM_DAPP = '0x10758d99D642428fd6A8B62A149aB2d1ade20C24';
const BLOCK_NUMBER = 8332856;

const provider = new ethers.providers.JsonRpcProvider(ETHEREUM_RPC);

const proofGenerator = new Ethereum.ProofGenerator(provider);

// EVM storage slot indexes (Each slot index is identified by 32 bytes)
// - slot 0 ...
// - slot 1 ...
// - slot 2 ...
// - slot 3 ...
// - slot 4 ...
// - slot 5 -> mapping(uint => bytes) destination_registry;
// - slot 6 -> mapping(uint => uint) amount_registry;
const destinationRegistryIndex = '5'.padStart(64, '0');
const amountRegistryIndex = '6'.padStart(64, '0');

// Key RLP encoded
const keyRLP = '0x01';

// Storage slots
// - Each mapping slot is the result of keccak256(<rlp_key> +  <slot_index>)
const destinationSlot = ethers.utils.keccak256(keyRLP + destinationRegistryIndex);
const amountSlot = ethers.utils.keccak256(keyRLP + amountRegistryIndex);

proofGenerator.generateStorageProof(ETHEREUM_DAPP, [destinationSlot, amountSlot], BLOCK_NUMBER).then(console.log);
```
