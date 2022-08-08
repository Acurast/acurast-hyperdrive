import { ContractAbstraction } from '@taquito/taquito';
export interface TezosProof {
    level: number;
    merkle_root: string;
    key: string;
    value: string;
    proof: [string, string][];
    signatures: [string, string][];
}
export declare function generateTezosProof(contract: ContractAbstraction<any>, owner: string, key: string, blockLevel: number): Promise<TezosProof>;
