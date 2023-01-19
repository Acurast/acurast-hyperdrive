import { ethers, providers } from 'ethers';

export interface EthereumStorageProof {
    block_number: number;
    account_proof_rlp: string;
    storage_proofs_rlp: string[];
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

export class ProofGenerator {
    constructor(private provider: providers.JsonRpcProvider) {}

    async generateStorageProof(
        contract: string,
        slots: string[],
        block_number?: number,
    ): Promise<EthereumStorageProof> {
        block_number ||= await this.provider.getBlockNumber();

        const proof = await this.provider.send('eth_getProof', [contract, slots, '0x' + block_number.toString(16)]);

        const account_proof_rlp = ethers.utils.RLP.encode(
            proof.accountProof.map((node: string) => ethers.utils.RLP.decode(node)),
        );

        const storage_proofs_rlp = slots.map((_, i) =>
            ethers.utils.RLP.encode(proof.storageProof[i].proof.map((node: string) => ethers.utils.RLP.decode(node))),
        );

        return {
            block_number,
            account_proof_rlp,
            storage_proofs_rlp,
        };
    }
}
