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
    proof: [string, string][];
}

export class Contract {
    constructor(private sdk: TezosToolkit, private contractAddress: string) {}

    async getStorage(block = 'head'): Promise<StateAggregatorStorage> {
        const script = await this.sdk.rpc.getScript(this.contractAddress, { block });
        const contractSchema = Schema.fromRPCResponse({ script: script });

        return contractSchema.Execute(script.storage, smartContractAbstractionSemantic(this.sdk.contract));
    }

    // async generateProof(owner: string, key: string, blockLevel: number): Promise<TezosProof> {
    //     const contract = await this.sdk.contract.at(this.contractAddress);

    //     const proof = await contract.contractViews
    //         .get_proof({ key, owner, level: blockLevel })
    //         .executeView({ viewCaller: owner });

    //     console.log(proof.proof);
    //     const blindedPath = proof.proof.reduce(() => {
    //         // TODO
    //     }, []);

    //     return {
    //         level: proof.level.toNumber(),
    //         merkle_root: '0x' + proof.merkle_root,
    //         key: '0x' + proof.key,
    //         value: '0x' + proof.value,
    //         proof: blindedPath,
    //     };
    // }

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

        const data: any = result.data;

        const blindedPath = data.args[2].reduce(() => {
            // TODO
        }, []);

        return {
            key: '0x' + data.args[0].bytes,
            merkle_root: '0x' + data.args[1].bytes,
            proof: blindedPath,
            snapshot: BigNumber(data.args[3].int),
            value: '0x' + data.args[4].bytes,
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
