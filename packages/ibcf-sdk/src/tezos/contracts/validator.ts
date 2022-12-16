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

export async function getStorage(
    tezos_sdk: TezosToolkit,
    validator_address: string,
    block = 'head',
): Promise<ValidatorStorage> {
    const script = await tezos_sdk.rpc.getScript(validator_address, { block });
    const contractSchema = Schema.fromRPCResponse({ script: script });

    return contractSchema.Execute(script.storage, smartContractAbstractionSemantic(tezos_sdk.contract));
}

/**
 * Submit the state root associated with a given ethereum block.
 */
export async function submit_block_state_root(
    tezos_sdk: TezosToolkit,
    state_aggregator_address: string,
    block_level: number,
    state_root: string,
): Promise<ContractMethod<ContractProvider>> {
    const contract = await tezos_sdk.contract.at(state_aggregator_address);

    return contract.methods.submit_block_state_root(block_level, state_root);
}
