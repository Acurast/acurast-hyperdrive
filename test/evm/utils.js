const crypto = require('crypto');
const ecPem  = require('ec-pem');

function signContent(keyPair, content) {
    // Create signature.
    const signer = crypto.createSign('RSA-SHA256');
    signer.update(content);
    let sigString = signer.sign(keyPair.encodePrivateKey(), 'hex');

    // Reformat signature / extract coordinates.
    const xlength = 2 * ('0x' + sigString.slice(6, 8));
    sigString = sigString.slice(8)

    return [
        '0x' + sigString.slice(0, xlength),
        '0x' + sigString.slice(xlength + 4)
    ];
}

function createSecp256r1KeyPair() {
    // Create curve object for key and signature generation.
    const prime256v1 = crypto.createECDH('prime256v1');
    prime256v1.generateKeys();
    const public_key = [
        '0x' + prime256v1.getPublicKey('hex').slice(2, 66),
        '0x' + prime256v1.getPublicKey('hex').slice(-64)
    ];
    // Reformat keys.
    pemFormattedKeyPair = ecPem(prime256v1, 'prime256v1');

    return [public_key, pemFormattedKeyPair]
}

function buildBuffer(...args) {
    return args.reduce((c, v) => {
        if(typeof v == "number") {
            return  Buffer.concat([c, Buffer.from((v).toString(16).padStart(64, "0"), "hex")])
        }
        return Buffer.concat([c, Buffer.from(v.slice(2), "hex")])
    }, Buffer.from([]))
}

async function expectsFailure(call, msg) {
    try {
        await call()
    } catch {
        return true;
    }

    throw new Error(msg || "Expected to fail, but passed.")
}

module.exports = {
    expectsFailure,
    buildBuffer,
    signContent,
    createSecp256r1KeyPair
}
