import { Schema } from '@taquito/michelson-encoder';
import { BigMapAbstraction, ContractMethod, ContractProvider, TezosToolkit } from '@taquito/taquito';
import { smartContractAbstractionSemantic } from './semantic';
import BigNumber from 'bignumber.js';
import { ethers } from 'ethers';

export interface BridgeStorage {
    nonce: BigNumber;
    wrap_nonce: BigMapAbstraction;
    registry: BigMapAbstraction;
    merkle_aggregator: string;
    proof_validator: string;
    asset_address: string;
    eth_bridge_address: string;
}

interface WrapArgument {
    block_number: string;
    nonce: string;
    account_proof_rlp: string;
    destination_proof_rlp: string;
    amount_proof_rlp: string;
}

export interface UnwrapArgument {
    destination: string;
    amount: string;
}

export interface Unwrap {
    level: BigNumber;
    nonce: BigNumber;
    destination: string;
    amount: BigNumber;
}

export class Contract {
    constructor(private sdk: TezosToolkit, private contractAddress: string) {}

    async getStorage(block = 'head'): Promise<BridgeStorage> {
        const script = await this.sdk.rpc.getScript(this.contractAddress, { block });
        const contractSchema = Schema.fromRPCResponse({ script: script });

        return contractSchema.Execute(script.storage, smartContractAbstractionSemantic(this.sdk.contract));
    }

    async getUnwraps(): Promise<Unwrap[]> {
        const storage = await this.getStorage();

        const unwraps: Unwrap[] = [];
        for (let i = 1; storage.nonce.gte(i); i++) {
            try {
                const unwrap = await storage.registry.get<Unwrap>(i);
                if (unwrap) {
                    unwraps.push({
                        ...unwrap,
                        nonce: BigNumber(i),
                    });
                }
            } catch {
                //
            }
        }

        return unwraps;
    }

    async wrap(argument: WrapArgument): Promise<ContractMethod<ContractProvider>> {
        const contract = await this.sdk.contract.at(this.contractAddress);

        return contract.methods.wrap(
            argument.account_proof_rlp,
            argument.amount_proof_rlp,
            argument.block_number,
            argument.destination_proof_rlp,
            argument.nonce,
        );
    }

    async unwrap(argument: UnwrapArgument): Promise<ContractMethod<ContractProvider>> {
        const contract = await this.sdk.contract.at(this.contractAddress);

        return contract.methods.unwrap(argument.amount, argument.destination);
    }

    computeUnwrapProofKey(nonce: number) {
        let rlpNonce = nonce.toString(16);
        rlpNonce = '0x' + (rlpNonce.length % 2 == 0 ? rlpNonce : '0' + rlpNonce);
        return ethers.utils.RLP.encode(rlpNonce).slice(2);
    }
}
