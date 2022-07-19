var ethers = require('ethers');

console.log(process.argv[2])

// The message...
var message = "Hello World";

// Sign the message (this could also come from eth_signMessage)
var wallet = new ethers.Wallet(privateKey);
var signature = wallet.signMessage(message)
// Split the signature into its r, s and v (Solidity's format)
var sig = ethers.utils.splitSignature(signature);
// Call the contract with the message and signature
var promise = contract.verifyString(message, sig.v, sig.r, sig.s);
promise.then(function(signer) {
    // Check the computed signer matches the actual signer
    console.log(signer === wallet.address);
});
