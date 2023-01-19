import { MichelsonMap, Schema } from '@taquito/michelson-encoder';
import { BigMapAbstraction, ContractMethod, ContractProvider, TezosToolkit } from '@taquito/taquito';
import { smartContractAbstractionSemantic } from './semantic';
import BigNumber from 'bignumber.js';

export interface StateAggregatorStorage {
    config: {
        administrator: string;
        max_state_size: BigNumber;
        snapshot_duration: BigNumber;
    };
    merkle_tree: {
        root: string;
        states: MichelsonMap<string, string>;
    };
    snapshot_counter: BigNumber;
    snapshot_level: BigMapAbstraction;
    snapshot_start_level: BigNumber;
}

export interface TezosProof {
    snapshot: BigNumber;
    merkle_root: string;
    key: string;
    value: string;
    path: [string, string][];
}

export class Contract {
    constructor(private sdk: TezosToolkit, private contractAddress: string) {}

    async getStorage(block = 'head'): Promise<StateAggregatorStorage> {
        const script = await this.sdk.rpc.getScript(this.contractAddress, { block });
        const contractSchema = Schema.fromRPCResponse({ script: script });

        return contractSchema.Execute(script.storage, smartContractAbstractionSemantic(this.sdk.contract));
    }

    async getProof(owner: string, key: string, blockLevel: string): Promise<TezosProof> {
        const result = await this.sdk.rpc.runScriptView(
            {
                contract: this.contractAddress,
                input: {
                    prim: 'Pair',
                    args: [{ bytes: key.replace('0x', '') }, { string: owner }],
                },
                view: 'get_proof',
                chain_id: await this.sdk.rpc.getChainId(),
            },
            { block: blockLevel },
        );

        const pair: any = result.data;
        const null_node = '0x0000000000000000000000000000000000000000000000000000000000000000';
        const blindedPath = (pair.args[2] as any[]).reduce<[string, string][]>((acc, { prim, args }) => {
            const node = '0x' + args[0].bytes;
            return [...acc, [prim == 'Left' ? node : null_node, prim == 'Right' ? node : null_node]];
        }, []);

        return {
            key: '0x' + pair.args[0].bytes,
            merkle_root: '0x' + pair.args[1].bytes,
            path: blindedPath,
            snapshot: BigNumber(pair.args[3].int),
            value: '0x' + pair.args[4].bytes,
        };
    }

    /**
     * Snapshot the current state and start a new one.
     */
    async snapshot(): Promise<ContractMethod<ContractProvider>> {
        const contract = await this.sdk.contract.at(this.contractAddress);

        return contract.methods.snapshot();
    }
}
