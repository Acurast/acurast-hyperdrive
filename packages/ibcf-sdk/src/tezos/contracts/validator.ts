import { MichelsonMap, Schema } from '@taquito/michelson-encoder';
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

export interface Snapshot {
    block_number: number;
    merkle_root: string;
}

export class Contract {
    constructor(private sdk: TezosToolkit, private contractAddress: string) {}

    async getStorage(block = 'head'): Promise<ValidatorStorage> {
        const script = await this.sdk.rpc.getScript(this.contractAddress, { block });
        const contractSchema = Schema.fromRPCResponse({ script: script });

        return contractSchema.Execute(script.storage, smartContractAbstractionSemantic(this.sdk.contract));
    }

    /**
     * Get the latest finalized snapshot.
     */
    async latestSnapshot(): Promise<Snapshot> {
        const storage = await this.getStorage();

        const latestBlockLevel = storage.history.pop();
        if (!latestBlockLevel) {
            throw new Error('No snapshots yet.');
        }
        const submissions = (await storage.state_root.get<MichelsonMap<string, string>>(latestBlockLevel)) || [];

        let merkleRoot = '';
        const distinct: Record<string, number> = {};
        for (const submission of submissions?.values()) {
            distinct[submission] ||= 0;
            distinct[submission] += 1;
            if (!distinct[merkleRoot] || distinct[merkleRoot] < distinct[submission]) {
                merkleRoot = submission;
            }
        }

        return {
            block_number: latestBlockLevel.toNumber(),
            merkle_root: '0x' + merkleRoot,
        };
    }

    /**
     * Submit the state root associated with a given ethereum block.
     */
    async submitBlockStateRoot(block_level: number, state_root: string): Promise<ContractMethod<ContractProvider>> {
        const contract = await this.sdk.contract.at(this.contractAddress);

        return contract.methods.submit_block_state_root(block_level, state_root);
    }
}
