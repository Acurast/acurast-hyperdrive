import { createContext } from 'react';
import type { BigNumber } from 'bignumber.js';
import { BigMapAbstraction } from '@taquito/taquito';
import { Ethereum, Tezos } from 'ibcf-sdk';

export interface TezosValidatorInfo {
    latestSnapshot: Tezos.Contracts.Validator.Snapshot;
}

export interface TezosBridgeStorage {
    asset: AssetInfo;
    unwraps: Tezos.Contracts.Bridge.Unwrap[];
}

export interface TezosStateAggregatorInfo {
    snapshot_level: BigMapAbstraction;
    merkle_tree: any;
}

export interface AssetInfo {
    address: string;
    balance: string;
}

export interface EVMBridgeInfo {
    asset: AssetInfo;
    wraps: Ethereum.Contracts.Bridge.Wrap[];
}

export interface EVMValidatorInfo {
    latestSnapshot: Ethereum.Contracts.Validator.Snapshot;
}

export interface IAppContext {
    tezos: {
        bridgeStorage?: TezosBridgeStorage;
        validatorInfo?: TezosValidatorInfo;
        stateAggregatorInfo?: TezosStateAggregatorInfo;
    };
    ethereum: {
        bridgeInfo?: EVMBridgeInfo;
        validatorInfo?: EVMValidatorInfo;
    };
}

const contextStub = {
    tezos: {},
    ethereum: {},
};

const AppContext = createContext<IAppContext>(contextStub);

export default AppContext;
