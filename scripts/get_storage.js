const Web3 = require('web3');
const web3_sdk = new Web3("https://goerli.infura.io/v3/d100ca58b1cc4ea98873b4f0ddd7894c");

(async () => {
    console.log(await new web3_sdk.eth.Contract([
    {
        inputs: [],
        name: 'getBalance',
        outputs: [
            {
                internalType: 'uint256',
                name: '',
                type: 'uint256',
            },
        ],
        stateMutability: 'view',
        type: 'function',
    },
], "0xabbfD1b3339C8B02e769BD8E8FdD3B1B6cc0426F").methods.getBalance().call())
})()
