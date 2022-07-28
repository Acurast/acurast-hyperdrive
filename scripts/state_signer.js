const crypto = require('crypto');
const ecPem  = require('ec-pem');
const { packDataBytes } = require("@taquito/michel-codec");
const { encodeExpr, b58cdecode, b58cencode } = require("@taquito/utils");
const { TezosToolkit } = require("@taquito/taquito");
const { InMemorySigner } = require("@taquito/signer");

const eth_private_key = "e8529dd47ef64bf253e46ac47a572abe0e2c87a6ee441eef708dde07ee7a382c";
const Tezos = new TezosToolkit("https://tezos-ithacanet-node-1.diamond.papers.tech");
const ibcf_tezos_aggregator = process.env["ADDRESS"] || "KT1UtaDDuiN1sMgpqMq2Wo4pVe1z7poZ4Loo";
let chain_id = ""

let big_map_id = -1;
const pending = new Map();
let latest_level = -1;
const [public_key, private_key] = loadSecp256r1KeyPair();

function packNat(nat) {
    return packDataBytes({ int: nat }, { prim: "nat" })
}

function buildContent(...args) {
    return args.reduce((c, v) => {
        if(typeof v == "number") {
            return  Buffer.concat([c, Buffer.from((v).toString(16).padStart(64, "0"), "hex")])
        }
        return Buffer.concat([c, Buffer.from(v.startsWith("0x") ? v.slice(2) : v, "hex")])
    }, Buffer.from([]))
}

function signContent(level, merkle_root) {
    // Create signature.
    const signer = crypto.createSign('RSA-SHA256');
    signer.update(buildContent(chain_id, level, merkle_root));
    let sigString = signer.sign(private_key, 'hex');

    // Reformat signature / extract coordinates.
    const xlength = 2 * ('0x' + sigString.slice(6, 8));
    sigString = sigString.slice(8)

    return [
        sigString.slice(0, xlength),
        sigString.slice(xlength + 4)
    ];
}

function loadSecp256r1KeyPair() {
    // Create curve object for key and signature generation.
    const prime256v1 = crypto.createECDH('prime256v1');
    prime256v1.setPrivateKey(Buffer.from(eth_private_key, "hex"));
    const public_key = [
        '0x' + prime256v1.getPublicKey('hex').slice(2, 66),
        '0x' + prime256v1.getPublicKey('hex').slice(-64)
    ];
    // Reformat keys.
    pemFormattedKeyPair = ecPem(prime256v1, 'prime256v1');

    return [public_key, pemFormattedKeyPair.encodePrivateKey()]
}

async function verifyPending() {
    const contract = await Tezos.contract.at(ibcf_tezos_aggregator)
    pending.forEach(async (v, level) => {
        const [r, s] = signContent(level, v.merkle_root);
        await contract.methods.submit_signature(level, r, s).send();
        pending.delete(level);
        console.log(`Signed merkle root '${v.merkle_root}' generated at level ${level}.`);
    });
}

async function monitor() {
    if (latest_level == 0) {
        const block = await Tezos.rpc.getBlockHeader();
        latest_level = block.level;
    } else {
        const block = await Tezos.rpc.getBlockHeader({ block: latest_level + 1 });
        latest_level = block.level;
    }

    verifyPending();

    const merkle_tree = await Tezos.rpc.getBigMapExpr(big_map_id, encodeExpr(packNat(latest_level).bytes));
    const merkle_root = merkle_tree["args"][1]["bytes"];

    pending.set(latest_level, {
        merkle_root,
    });
}

(async () => {
    Tezos.setProvider({ signer: await InMemorySigner.fromSecretKey(process.env["PRIVATE_KEY"]) });
    chain_id = b58cdecode(await Tezos.rpc.getChainId(), new Uint8Array([0x87,0x82,0x00])).toString("hex");

    const storage = await Tezos.rpc.getStorage(ibcf_tezos_aggregator);
    big_map_id = storage["args"][2]["int"];

    (async function loop() {
        await new Promise(r => setTimeout(r, 5000))
        monitor().then(loop).catch(e=>{ loop()})
    })();
})()
