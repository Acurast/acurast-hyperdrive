import { Schema } from '@taquito/michelson-encoder';
import { BigMapAbstraction, ContractMethod, ContractProvider, TezosToolkit } from '@taquito/taquito';
import { smartContractAbstractionSemantic } from './semantic';
import BigNumber from 'bignumber.js';

export interface ValidatorStorage {
    config: {
        administrator: string;
        validators: string[];
        minimum_endorsements: BigNumber;
        history_length: BigNumber;
        snapshot_interval: BigNumber;
    };
    current_snapshot: BigNumber;
    state_root: BigMapAbstraction;
    history: BigNumber[];
}

export class Contract {
    constructor(private sdk: TezosToolkit, private contractAddress: string) {}

    async getStorage(block = 'head'): Promise<ValidatorStorage> {
        const script = await this.sdk.rpc.getScript(this.contractAddress, { block });
        const contractSchema = Schema.fromRPCResponse({ script: script });

        return contractSchema.Execute(script.storage, smartContractAbstractionSemantic(this.sdk.contract));
    }

    /**
     * Submit the state root associated with a given ethereum block.
     */
    async submit_block_state_root(block_level: number, state_root: string): Promise<ContractMethod<ContractProvider>> {
        const contract = await this.sdk.contract.at(this.contractAddress);

        return contract.methods.submit_block_state_root(block_level, state_root);
    }
}
