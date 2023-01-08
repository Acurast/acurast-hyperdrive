import Web3 from 'web3';
import RLP from 'rlp';

export function getProofKey(eth_address: string, nonce: number): string {
    const bytes = Web3.utils.bytesToHex(Array.from(RLP.encode([eth_address, nonce])));
    const key = Web3.utils.sha3(bytes);
    if (!key) {
        throw new Error('Could not compute proof key.');
    }
    return key;
}
