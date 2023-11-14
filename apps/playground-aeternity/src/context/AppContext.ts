import { createContext } from 'react';
import type { BigNumber } from 'bignumber.js';
import { BigMapAbstraction } from '@taquito/taquito';
import { Ethereum, Tezos } from 'ibcf-sdk';

export enum Network {
    Ethereum = 'ethereum-sepolia',
}

export interface BridgeMovement {
    nonce: bigint;
    amount: bigint;
    destination: string;
    sender: string;
}

export interface AeternityBridgeInfo {
    asset: AssetInfo;
    movements: BridgeMovement[];
}

export interface TezosFundingEvent {
    funder: string;
    amount: number;
}

export interface AssetInfo {
    address: string;
    balance: string;
}

export interface EVMBridgeInfo {
    asset: AssetInfo;
    movements: BridgeMovement[];
}

export interface FundEvent {
    funder: string;
    amount: BigNumber;
    nonce: BigNumber;
}

export interface IAppContext {
    network: Network;
    updateNetwork: (network: Network) => void;
    aeternity: {
        bridgeInfo?: AeternityBridgeInfo;
    };
    ethereum: {
        bridgeInfo?: EVMBridgeInfo;
    };
}

const contextStub = {
    network: Network.Ethereum,
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    updateNetwork: () => {},
    aeternity: {},
    ethereum: {},
};

const AppContext = createContext<IAppContext>(contextStub);

export default AppContext;
