import { createContext } from 'react';
import type { BigNumber } from 'bignumber.js';
import { BigMapAbstraction } from '@taquito/taquito';
import { Blueprint } from '@ibcf/sdk';

export interface TezosBridgeStorage {
    asset: AssetInfo;
}

export interface TezosStateAggregatorStorage {
    merkle_history_indexes: BigNumber[];
    merkle_history: BigMapAbstraction;
    blocks: [BigNumber, string][];
}

export interface AssetInfo {
    address: string;
    balance: string;
}

export interface EthereumStorage {
    asset: AssetInfo;
    wraps: Blueprint.Bridge.Wrap[];
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
