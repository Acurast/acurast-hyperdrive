const Web3Proofs = require('@aragon/web3-proofs')
const Web3 = require('web3');

const web3 = new Web3("https://mainnet.infura.io/v3/75829a5785c844bc9c9e6e891130ee6f");
const web3proofs = new Web3Proofs(web3.currentProvider)


const contract_address = "0x9cc9bf39a84998089050a90087e597c26758685d";
let block_number = 7179825;


(async ()=> {
    const proof = await web3proofs.getProof(contract_address, ["0x0"], block_number)
    console.log({
        contract_address: proof.proof.address,
        storage_slot: "0x" + proof.proof.storageProof[0].key.slice(2).padStart(32, "0"),
        block_proof_rlp: proof.blockHeaderRLP,
        account_proof_rlp: proof.accountProofRLP,
        storage_proof_rlp: proof.storageProofsRLP,
    })
})()
