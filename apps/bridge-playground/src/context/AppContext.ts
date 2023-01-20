import { createContext } from 'react';
import type { BigNumber } from 'bignumber.js';
import { BigMapAbstraction } from '@taquito/taquito';
import { Ethereum, Tezos } from 'ibcf-sdk';

export interface TezosBridgeStorage {
    asset: AssetInfo;
    unwraps: Tezos.Contracts.Bridge.Unwrap[];
}

export interface TezosStateAggregatorStorage {
    snapshot_level: BigMapAbstraction;
    merkle_tree: any;
    blocks: [BigNumber, string][];
}

export interface AssetInfo {
    address: string;
    balance: string;
}

export interface EthereumStorage {
    asset: AssetInfo;
    wraps: Ethereum.Contracts.Bridge.Wrap[];
}

export interface IAppContext {
    tezos: {
        bridgeStorage?: TezosBridgeStorage;
        validatorStorage?: [string, string][];
        stateAggregatorStorage?: TezosStateAggregatorStorage;
    };
    ethereum: {
        clientStorage?: EthereumStorage;
    };
}

const contextStub = {
    tezos: {},
    ethereum: {},
};

const AppContext = createContext<IAppContext>(contextStub);

export default AppContext;
