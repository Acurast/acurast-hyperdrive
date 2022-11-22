import type { Eth } from 'web3-eth';
import Web3 from 'web3';
import RLP from 'rlp';

import ABI from './abi';
import { Wrap } from '../common';

const STORAGE_SLOT = {
    asset: '01'.padStart(64, '00'),
    tezos_nonce: '03'.padStart(64, '00'),
    registry: '05'.padStart(64, '00'),
};

export { ABI };

export async function getAssetAddress(web3_eth: Eth, eth_bridge_address: string): Promise<string> {
    return (
        '0x' +
        (await web3_eth.getStorageAt(eth_bridge_address, STORAGE_SLOT.asset))
            .slice(2 /* remove 0x */)
            .slice(24 /* Addresses are 20 bytes long and evm storage segments data in chunks of 32 bytes */)
    );
}

export async function getWraps(web3_eth: Eth, eth_bridge_address: string): Promise<Wrap[]> {
    const contract = new web3_eth.Contract(ABI as any, eth_bridge_address);
    const wraps: Wrap[] = await contract
        .getPastEvents('Wrap', {
            fromBlock: 0,
            toBlock: 'latest', // You can also specify 'latest'
        })
        .then((events) =>
            events.map((event) => ({
                address: event.returnValues[0],
                amount: event.returnValues[1],
                nonce: event.returnValues[2],
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

// function getTeleportRegistryStorageKey(tezos_address: string, nonce: number) {
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
