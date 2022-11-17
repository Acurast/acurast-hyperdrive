import type { Eth } from 'web3-eth';
import Web3 from 'web3';

export class Ethereum {
    static STORAGE_SLOT = {
        tezos_nonce: '03'.padStart(64, '00'),
        registry: '05'.padStart(64, '00'),
    };

    static getTezosNonceStorageKey(tezos_address: string) {
        return Web3.utils.sha3(tezos_address + Ethereum.STORAGE_SLOT.tezos_nonce);
    }

    static getTeleportRegistryStorageKey(tezos_address: string, nonce: number) {
        const hexNonce = Web3.utils.toHex(nonce).slice(2).padStart(64, '0');
        return Web3.utils.sha3(tezos_address + hexNonce + Ethereum.STORAGE_SLOT.registry);
    }

    static async getTezosNonce(web3_eth: Eth, eth_bridge_address: string, tezos_address: string) {
        const indexKey = Ethereum.getTezosNonceStorageKey(tezos_address);

        if (!indexKey) {
            throw new Error('Invalid storage key.');
        }

        Web3.utils.toBN(await web3_eth.getStorageAt(eth_bridge_address, indexKey));
    }

    static async getTeleportAmount(web3_eth: Eth, eth_bridge_address: string, tezos_address: string, nonce: number) {
        const indexKey = Ethereum.getTeleportRegistryStorageKey(tezos_address, nonce);

        if (!indexKey) {
            throw new Error('Invalid storage key.');
        }

        Web3.utils.toBN(await web3_eth.getStorageAt(eth_bridge_address, indexKey));
    }
}
