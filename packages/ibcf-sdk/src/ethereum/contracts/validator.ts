import { TransactionResponse, Provider } from '@ethersproject/abstract-provider';
import { Signer } from '@ethersproject/abstract-signer';
import { Contract } from '@ethersproject/contracts';
import BigNumber from 'bignumber.js';
import ABI from './abi/validator.json';

export async function getCurrentSnapshot(provider: Provider, validator_address: string): Promise<BigNumber> {
    const contract = new Contract(validator_address, ABI, provider);

    return BigNumber((await contract.get_current_snapshot()).toString());
}

export async function getCurrentSnapshotSubmissions(provider: Provider, validator_address: string): Promise<string[]> {
    const contract = new Contract(validator_address, ABI, provider);

    return contract.get_current_snapshot_submissions();
}

export async function submitStateRoot(
    signer: Signer,
    validator_address: string,
    snapshot: BigNumber,
    state_root: string,
): Promise<TransactionResponse> {
    const contract = new Contract(validator_address, ABI, signer);

    return contract.submit_state_root(snapshot.toString(), state_root);
}
