import { TransactionResponse, Provider } from '@ethersproject/abstract-provider';
import { Signer } from '@ethersproject/abstract-signer';
import { Contract } from '@ethersproject/contracts';
import BigNumber from 'bignumber.js';
import ABI from './abi/validator.json';

const STORAGE_SLOT = {
    asset: '01'.padStart(64, '00'),
    tezos_nonce: '03'.padStart(64, '00'),
    registry: '05'.padStart(64, '00'),
};

export async function getAssetAddress(provider: Provider, bridge_address: string): Promise<string> {
    return (
        '0x' +
        (await provider.getStorageAt(bridge_address, STORAGE_SLOT.asset))
            .slice(2 /* remove 0x */)
            .slice(24 /* Addresses are 20 bytes long and evm storage segments data in chunks of 32 bytes */)
    );
}

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
