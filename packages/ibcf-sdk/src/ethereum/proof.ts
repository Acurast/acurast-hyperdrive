import { ethers } from 'ethers';

export interface EthereumProof {
    block_number: number;
    account_proof_rlp: string;
    storage_proof_rlp: string;
}

// function buildHeaderBytes(block: any) {
//     const fields = [
//         toBuffer(block.parentHash),
//         toBuffer(block.sha3Uncles),
//         toBuffer(block.miner),
//         toBuffer(block.stateRoot),
//         toBuffer(block.transactionsRoot),
//         toBuffer(block.receiptsRoot),
//         toBuffer(block.logsBloom),
//         toBuffer(ethers.utils.hexlify(block.difficulty)),
//         toBuffer(ethers.utils.hexlify(block.number)),
//         toBuffer(ethers.utils.hexlify(block.gasLimit)),
//         toBuffer(ethers.utils.hexlify(block.gasUsed)),
//         toBuffer(ethers.utils.hexlify(block.timestamp)),
//         toBuffer(block.extraData),
//         toBuffer(block.mixHash),
//         toBuffer(block.nonce),
//         toBuffer(ethers.utils.hexlify(block.baseFeePerGas)),
//     ];
//     return Buffer.from(ethers.utils.RLP.encode(fields)).toString('hex');
// }

export async function generateProof(
    provider: ethers.providers.JsonRpcProvider,
    address: string,
    slot: string,
    block_number: number,
): Promise<EthereumProof> {
    // const block = await web3_eth.getBlock(block_number);
    // const block_header_rlp = buildHeaderBytes(block);

    const proof = await provider.send('eth_getProof', [address, [slot], block_number]);
    const account_proof_rlp =
        '0x' +
        Buffer.from(
            ethers.utils.RLP.encode(proof.accountProof.map((node: string) => ethers.utils.RLP.decode(node)) as any),
        ).toString('hex');
    const storage_proof_rlp =
        '0x' +
        Buffer.from(
            ethers.utils.RLP.encode(
                proof.storageProof[0].proof.map((node: string) => ethers.utils.RLP.decode(node)) as any,
            ),
        ).toString('hex');

    return {
        //storage_slot: '0x' + proof.storageProof[0].key.slice(2).padStart(64, '0'),
        // state_root: block.stateRoot,
        // block_header_rlp: block_header_rlp,
        block_number,
        account_proof_rlp: account_proof_rlp,
        storage_proof_rlp: storage_proof_rlp,
    };
}
