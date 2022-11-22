import type { Eth } from 'web3-eth';
import Web3 from 'web3';
import RLP from 'rlp';

import type BN from 'bn.js';

export interface Wrap {
    address: string;
    amount: BN;
    nonce: number;
}

export * as Tezos from './tezos';
export * as Ethereum from './ethereum';
