import { createContext } from 'react';
import type { BigNumber } from 'bignumber.js';
import { BigMapAbstraction } from '@taquito/taquito';
import { Ethereum, Tezos } from 'ibcf-sdk';

export enum Network {
    Ethereum = 'ethereum-goerli',
    Polygon = 'polygon-mumbai',
    BSC = 'bsc-testnet',
    Avalanche = 'avalanche-testnet',
}

export interface TezosValidatorInfo {
    latestSnapshot: Tezos.Contracts.Validator.Snapshot;
}

export interface TezosBridgeInfo {
    asset: AssetInfo;
    unwraps: Tezos.Contracts.Bridge.Unwrap[];
}

export interface TezosFundingEvent {
    funder: string;
    amount: number;
}

export interface TezosCrowdfundInfo {
    tezos_funding: TezosFundingEvent[];
    eth_funding: TezosFundingEvent[];
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

export interface FundEvent {
    funder: string;
    amount: BigNumber;
    nonce: BigNumber;
}

export interface EVMCrowdfundInfo {
    funding: FundEvent[];
}

export interface IAppContext {
    network: Network;
    updateNetwork: (network: Network) => void;
    tezos: {
        bridgeInfo?: TezosBridgeInfo;
        validatorInfo?: TezosValidatorInfo;
        stateAggregatorInfo?: TezosStateAggregatorInfo;
        crowdfundInfo?: TezosCrowdfundInfo;
    };
    ethereum: {
        bridgeInfo?: EVMBridgeInfo;
        validatorInfo?: EVMValidatorInfo;
        crowdfundInfo?: EVMCrowdfundInfo;
    };
}

const contextStub = {
    network: Network.Ethereum,
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    updateNetwork: () => {},
    tezos: {},
    ethereum: {},
};

const AppContext = createContext<IAppContext>(contextStub);

export default AppContext;
