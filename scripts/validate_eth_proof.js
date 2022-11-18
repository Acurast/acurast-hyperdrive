const Web3 = require('web3');
const { Trie } = require('@ethereumjs/trie');
const RLP = require('rlp');

const trie = new Trie()
const web3_sdk = new Web3("https://goerli.infura.io/v3/d100ca58b1cc4ea98873b4f0ddd7894c");

const ETH_BRIDGE_ADDRESS = process.argv[2] || '0x0C2dBba45E207619B79Fd7946496fbEc1E66fA8C';

const ACCOUNT_STATE_ROOT_INDEX = 2;

const ETH_BLOCK_NUMBER = 7976909;
const tezos_address = "0x050a000000160000eaeec9ada5305ad61fc452a5ee9f7d4f55f80467"
const storageIndex = "05".padStart(64, '0');
const hexNonce = Web3.utils.toHex(1).slice(2).padStart(64, '0');
const storageSlot = Web3.utils.sha3(tezos_address + hexNonce + storageIndex);

(async () => {
    const [block, account] = await Promise.all([
        web3_sdk.eth.getBlock(ETH_BLOCK_NUMBER),
        web3_sdk.eth.getProof(ETH_BRIDGE_ADDRESS, [storageSlot], ETH_BLOCK_NUMBER)
    ])

    const blockStateRoot = Buffer.from(block.stateRoot.slice(2), 'hex');
    const acountkey = Buffer.from(Web3.utils.sha3(ETH_BRIDGE_ADDRESS).slice(2), 'hex');
    const accountProof = account.accountProof.map(x => Buffer.from(x.slice(2), 'hex'))
    const storageProof = account.storageProof[0].proof.map(x => Buffer.from(x.slice(2), 'hex'))

    const account_proof_rlp = Buffer.from(RLP.encode(account.accountProof.map((r) => RLP.decode(r)))).toString(
        'hex',
    );
    const storage_proof_rlp = Buffer.from(
        RLP.encode(account.storageProof[0].proof.map((r) => RLP.decode(r))),
    ).toString('hex');

    console.log({
        ETH_ACCOUNT_PROOF: account_proof_rlp,
        ETH_STORAGE_PROOF: storage_proof_rlp,
        ETH_BRIDGE_ADDRESS,
        ETH_BLOCK_NUMBER,
        ETH_BLOCK_ROOT_STATE: block.stateRoot,
    })

    try {
        const value = (await trie.verifyProof(blockStateRoot, acountkey, accountProof))

        // Validate account
        if (!value.equals(Buffer.from(RLP.encode([Number(account.nonce), Number(account.balance), account.storageHash, account.codeHash]))))
            console.log('proof failed')
        else
            console.log('Account proof is valid!')

            const accountStateRoot = RLP.decode(value)[ACCOUNT_STATE_ROOT_INDEX]
            const storage = (await trie.verifyProof(accountStateRoot, Buffer.from(Web3.utils.sha3(storageSlot).slice(2), 'hex'), storageProof))
            console.log('Storage:', storage)
    }catch(e) {
        console.log(e)
    }
})()
