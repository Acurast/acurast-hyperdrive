import { Signer } from '@ethersproject/abstract-signer';
import { Contract as EthersContract } from '@ethersproject/contracts';
import { JsonRpcProvider, TransactionResponse } from '@ethersproject/providers';
import BigNumber from 'bignumber.js';
import { ethers } from 'ethers';

import { unpackAddress } from '../../tezos/utils';
import { ProofGenerator } from '../proof';
import ABI from './abi/bridge.json';

export interface Wrap {
    address: string;
    amount: BigNumber;
    nonce: BigNumber;
}

export interface WrapProof {
    block_number: number;
    account_proof_rlp: string;
    destination_proof_rlp: string;
    amount_proof_rlp: string;
}

const STORAGE_SLOT = {
    asset: 1,
    tezos_nonce: 4,
    destination_registry: 5,
    amount_registry: 6,
};

export class Contract {
    private signer: Signer;
    private provider: JsonRpcProvider;
    private contractAddress: string;

    constructor(signer: Signer, contractAddress: string) {
        this.signer = signer;
        this.provider = signer.provider as JsonRpcProvider;
        this.contractAddress = contractAddress;
    }

    async getAssetAddress(): Promise<string> {
        return (
            '0x' +
            (await this.provider.getStorageAt(this.contractAddress, STORAGE_SLOT.asset))
                .slice(2 /* remove 0x */)
                .slice(24 /* Addresses are 20 bytes long and evm storage segments data in chunks of 32 bytes */)
        );
    }

    async getWraps(fromBlock: number | string = 0, toBlock: number | string = 'latest'): Promise<Wrap[]> {
        const contract = new EthersContract(this.contractAddress, ABI, this.provider);
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
                console.log('Err:', err);
                return [];
            });

        return wraps;
    }

    async unwrapProcessed(nonce: number): Promise<boolean> {
        const hexNonce = nonce.toString(16).padStart(64, '0');
        const tezosNonceIndex = STORAGE_SLOT.tezos_nonce.toString(16).padStart(64, '0');
        const slot = ethers.utils.keccak256('0x' + hexNonce + tezosNonceIndex);

        const result = await this.provider.getStorageAt(this.contractAddress, slot);
        return Number(result) == 1;
    }

    async generateWrapProof(hexNonce: string, block_number: number): Promise<WrapProof> {
        const destinationRegistryIndex = '05'.padStart(64, '0');
        const amountRegistryIndex = '06'.padStart(64, '0');
        const destinationSlot = ethers.utils.keccak256('0x' + hexNonce + destinationRegistryIndex);
        const amountSlot = ethers.utils.keccak256('0x' + hexNonce + amountRegistryIndex);

        const proofGenerator = new ProofGenerator(this.provider);

        const proof = await proofGenerator.generateStorageProof(
            this.contractAddress,
            [destinationSlot, amountSlot],
            block_number,
        );

        return {
            block_number,
            account_proof_rlp: proof.account_proof_rlp,
            destination_proof_rlp: proof.storage_proofs_rlp[0],
            amount_proof_rlp: proof.storage_proofs_rlp[1],
        };
    }

    async unwrap(snapshot: BigNumber, key: string, value: string, proof: string[][]): Promise<TransactionResponse> {
        const contract = new EthersContract(this.contractAddress, ABI, this.signer);

        return contract.unwrap(snapshot.toString(), key, value, proof);
    }
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
