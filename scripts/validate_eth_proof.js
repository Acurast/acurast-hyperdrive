const Web3 = require('web3');
const { Trie } = require('@ethereumjs/trie');
const RLP = require('rlp');

const trie = new Trie()
const web3_sdk = new Web3("https://goerli.infura.io/v3/d100ca58b1cc4ea98873b4f0ddd7894c");

const address = process.argv[2] || '0x15862e73957701C56892D8C689A6189A16c8e05d';

const ACCOUNT_STATE_ROOT_INDEX = 2;
const storageSlot = "0x346629535920ae179e6d13e36fe4643e45066f531ab311fee89999b8eb5d1d8f";

(async () => {
    const [block, account] = await Promise.all([
        web3_sdk.eth.getBlock(7934545),
        web3_sdk.eth.getProof(address, [storageSlot], 7934545)
    ])

    const blockStateRoot = Buffer.from(block.stateRoot.slice(2), 'hex');
    const acountkey = Buffer.from(Web3.utils.sha3(address).slice(2), 'hex');
    const accountProof = account.accountProof.map(x => Buffer.from(x.slice(2), 'hex'))
    const storageProof = account.storageProof[0].proof.map(x => Buffer.from(x.slice(2), 'hex'))

    const account_proof_rlp = Buffer.from(RLP.encode(account.accountProof.map((r) => RLP.decode(r)))).toString(
        'hex',
    );
    const storage_proof_rlp = Buffer.from(
        RLP.encode(account.storageProof[0].proof.map((r) => RLP.decode(r))),
    ).toString('hex');
    console.log(account_proof_rlp, storage_proof_rlp)

    try {
        const value = (await trie.verifyProof(blockStateRoot, acountkey, accountProof))

        // Validate account
        if (!value.equals(Buffer.from(RLP.encode([Number(account.nonce), Number(account.balance), account.storageHash, account.codeHash]))))
            console.log('proof failed')
        else
            console.log('Account proof is valid|!')

            const accountStateRoot = RLP.decode(value)[ACCOUNT_STATE_ROOT_INDEX]
            const storage = (await trie.verifyProof(accountStateRoot, Buffer.from(Web3.utils.sha3(storageSlot).slice(2), 'hex'), storageProof))
            console.log('Storage:', storage)
    }catch(e) {
        console.log(e)
    }
})()
