import Web3 from 'web3';
import type { Eth } from 'web3-eth';
import * as RLP from 'rlp';
import { toBuffer } from 'eth-util-lite';

export interface EthereumProof {
    block_number: number;
    account_proof_rlp: string;
    storage_proof_rlp: string;
}

function buildHeaderBytes(block: any) {
    const fields = [
        toBuffer(block.parentHash),
        toBuffer(block.sha3Uncles),
        toBuffer(block.miner),
        toBuffer(block.stateRoot),
        toBuffer(block.transactionsRoot),
        toBuffer(block.receiptsRoot),
        toBuffer(block.logsBloom),
        toBuffer(Web3.utils.toHex(block.difficulty)),
        toBuffer(Web3.utils.toHex(block.number)),
        toBuffer(Web3.utils.toHex(block.gasLimit)),
        toBuffer(Web3.utils.toHex(block.gasUsed)),
        toBuffer(Web3.utils.toHex(block.timestamp)),
        toBuffer(block.extraData),
        toBuffer(block.mixHash),
        toBuffer(block.nonce),
        toBuffer(Web3.utils.toHex(block.baseFeePerGas)),
    ];
    return Buffer.from(RLP.encode(fields)).toString('hex');
}

export async function generateEthereumProof(
    web3_eth: Eth,
    address: string,
    slot: string,
    block_number: number,
): Promise<EthereumProof> {
    // const block = await web3_eth.getBlock(block_number);
    // const block_header_rlp = buildHeaderBytes(block);

    const proof = await web3_eth.getProof(address, [slot], block_number);
    const account_proof_rlp = Buffer.from(RLP.encode(proof.accountProof.map((r) => RLP.decode(r)) as any)).toString(
        'hex',
    );
    const storage_proof_rlp = Buffer.from(
        RLP.encode(proof.storageProof[0].proof.map((r) => RLP.decode(r)) as any),
    ).toString('hex');

    console.log(proof);

    return {
        //storage_slot: '0x' + proof.storageProof[0].key.slice(2).padStart(64, '0'),
        // state_root: block.stateRoot,
        // block_header_rlp: block_header_rlp,
        block_number,
        account_proof_rlp: account_proof_rlp,
        storage_proof_rlp: storage_proof_rlp,
    };
}
