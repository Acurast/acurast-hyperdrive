var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import Web3 from 'web3';
import * as RLP from 'rlp';
import { toBuffer } from 'eth-util-lite';
function buildHeaderBytes(block) {
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
export function generateEthereumProof(web3_eth, address, slot, block_number) {
    return __awaiter(this, void 0, void 0, function* () {
        const block = yield web3_eth.getBlock(block_number);
        // const block_header_rlp = buildHeaderBytes(block);
        const proof = yield web3_eth.getProof(address, [slot], block_number);
        const account_proof_rlp = Buffer.from(RLP.encode(proof.accountProof.map((r) => RLP.decode(r)))).toString('hex');
        const storage_proof_rlp = Buffer.from(RLP.encode(proof.storageProof[0].proof.map((r) => RLP.decode(r)))).toString('hex');
        return {
            //storage_slot: '0x' + proof.storageProof[0].key.slice(2).padStart(64, '0'),
            // state_root: block.stateRoot,
            // block_header_rlp: block_header_rlp,
            block_number,
            account_proof_rlp: account_proof_rlp,
            storage_proof_rlp: storage_proof_rlp,
        };
    });
}
