import type BN from 'bn.js';

export interface Wrap {
    address: string;
    amount: BN;
    nonce: number;
}

export * as Tezos from './tezos';
