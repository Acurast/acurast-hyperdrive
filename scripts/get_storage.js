const Web3 = require('web3');
const web3_sdk = new Web3("https://goerli.infura.io/v3/d100ca58b1cc4ea98873b4f0ddd7894c");

const address = process.argv[2] || '0xE83051942Da40421021B9CBBfB007038A1F32614'

web3_sdk.eth.getStorageAt(address, 0).then(web3_sdk.utils.toAscii).then(storage => console.log("Counter:", storage));
