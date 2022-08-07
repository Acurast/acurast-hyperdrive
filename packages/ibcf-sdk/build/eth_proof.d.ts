import type { Eth } from 'web3-eth';
export interface EthereumProof {
    block_number: number;
    account_proof_rlp: string;
    storage_proof_rlp: string;
}
export declare function generateEthereumProof(web3_eth: Eth, address: string, slot: string, block_number: number): Promise<EthereumProof>;
