import { createContext } from 'react';
import type { BigNumber } from 'bignumber.js';

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
    account: string;
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
