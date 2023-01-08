import { Provider } from '@ethersproject/abstract-provider';
import { Signer } from '@ethersproject/abstract-signer';
import { Contract } from '@ethersproject/contracts';
import BigNumber from 'bignumber.js';
import { unpackAddress } from '../../tezos/utils';
import ABI from './abi/bridge.json';

export interface Wrap {
    address: string;
    amount: BigNumber;
    nonce: BigNumber;
}

const STORAGE_SLOT = {
    asset: 1,
    tezos_nonce: 3,
    registry: 5,
};

export async function getAssetAddress(provider: Provider, eth_bridge_address: string): Promise<string> {
    return (
        '0x' +
        (await provider.getStorageAt(eth_bridge_address, STORAGE_SLOT.asset))
            .slice(2 /* remove 0x */)
            .slice(24 /* Addresses are 20 bytes long and evm storage segments data in chunks of 32 bytes */)
    );
}

export async function getWraps(
    provider: Provider,
    eth_bridge_address: string,
    fromBlock = 0,
    toBlock: number | string = 'latest',
): Promise<Wrap[]> {
    const contract = new Contract(eth_bridge_address, ABI, provider);
    const wraps: Wrap[] = await contract
        .queryFilter(contract.filters.Wrap(), fromBlock, toBlock)
        .then((events) =>
            events.map((event) => ({
                address: unpackAddress(event.args?.[0]),
                amount: BigNumber(event.args?.[1].toString()),
                nonce: BigNumber(event.args?.[2].toString()),
            })),
        )
        .catch((err) => {
            console.log(err);
            return [];
        });

    return wraps;
}

// function getTezosNonceStorageKey(tezos_address: string) {
//     return Web3.utils.sha3(tezos_address + STORAGE_SLOT.tezos_nonce);
// }

// export function getWrapRegistryStorageKey(tezos_address: string, nonce: number) {
//     const hexNonce = Web3.utils.toHex(nonce).slice(2).padStart(64, '0');
//     return Web3.utils.sha3(tezos_address + hexNonce + STORAGE_SLOT.registry);
// }

// async function getTezosNonce(web3_eth: Eth, eth_bridge_address: string, tezos_address: string) {
//     const indexKey = getTezosNonceStorageKey(tezos_address);

//     if (!indexKey) {
//         throw new Error('Invalid storage key.');
//     }

//     return Web3.utils.toBN(await web3_eth.getStorageAt(eth_bridge_address, indexKey));
// }

// async function getWrappedAmount(web3_eth: Eth, eth_bridge_address: string, tezos_address: string, nonce: number) {
//     const indexKey = getTeleportRegistryStorageKey(tezos_address, nonce);

//     if (!indexKey) {
//         throw new Error('Invalid storage key.');
//     }

//     return Web3.utils.toBN(await web3_eth.getStorageAt(eth_bridge_address, indexKey));
// }
