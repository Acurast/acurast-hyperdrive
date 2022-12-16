import { MichelsonMap, Schema } from '@taquito/michelson-encoder';
import {
    BigMapAbstraction,
    ContractMethod,
    ContractProvider,
    TezosToolkit,
    TransactionOperation,
} from '@taquito/taquito';
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

export async function getStorage(
    tezos_sdk: TezosToolkit,
    validator_address: string,
    block = 'head',
): Promise<StateAggregatorStorage> {
    const script = await tezos_sdk.rpc.getScript(validator_address, { block });
    const contractSchema = Schema.fromRPCResponse({ script: script });

    return contractSchema.Execute(script.storage, smartContractAbstractionSemantic(tezos_sdk.contract));
}

export interface TezosProof {
    level: number;
    merkle_root: string;
    key: string;
    value: string;
    proof: [string, string][];
    signatures: [string, string][];
}

export async function getProof(
    tezos_sdk: TezosToolkit,
    state_aggregator_address: string,
    owner: string,
    key: string,
    blockLevel: string,
): Promise<any> {
    const storage = await tezos_sdk.rpc.runScriptView(
        {
            contract: state_aggregator_address,
            input: { prim: 'Unit' },
            view: 'get_proof',
            chain_id: await tezos_sdk.rpc.getChainId(),
        },
        { block: blockLevel },
    );

    console.log(storage);

    return '';
}

/**
 * Snapshot the current state and start a new one.
 */
export async function snapshot(
    tezos_sdk: TezosToolkit,
    state_aggregator_address: string,
): Promise<ContractMethod<ContractProvider>> {
    const contract = await tezos_sdk.contract.at(state_aggregator_address);

    return contract.methods.snapshot();
}
