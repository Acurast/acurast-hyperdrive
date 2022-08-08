import { createContext } from 'react';
import type { BigNumber } from 'bignumber.js';
import { BigMapAbstraction } from '@taquito/taquito';

export interface TezosClientStorage {
    counter: BigNumber;
    eth_contract: string;
    ibcf_eth_validator: string;
    ibcf_tezos_state: string;
    storage_slot: string;
}

export interface TezosStateAggregatorStorage {
    merkle_history_indexes: BigNumber[];
    merkle_history: BigMapAbstraction;
    blocks: [BigNumber, string][];
}

export interface EthereumClientStorage {
    counter: string;
}

export interface IAppContext {
    tezos: {
        clientStorage?: TezosClientStorage;
        validatorStorage?: [string, string][];
        stateAggregatorStorage?: TezosStateAggregatorStorage;
    };
    ethereum: {
        clientStorage?: EthereumClientStorage;
    };
}

const contextStub = {
    tezos: {},
    ethereum: {},
};

const AppContext = createContext<IAppContext>(contextStub);

export default AppContext;
