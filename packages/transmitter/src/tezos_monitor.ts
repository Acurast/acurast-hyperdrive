import crypto from 'crypto';
import ecPem from 'ec-pem';
import { b58cdecode } from '@taquito/utils';
import { BigMapAbstraction, ContractAbstraction, MichelsonMap, TezosToolkit } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';

function buildContent(...args: (string | number)[]) {
    return args.reduce((c, v) => {
        if (typeof v == 'number') {
            return Buffer.concat([c, Buffer.from(v.toString(16).padStart(64, '0'), 'hex')]);
        }
        return Buffer.concat([c, Buffer.from(v.startsWith('0x') ? v.slice(2) : v, 'hex')]);
    }, Buffer.from([]));
}

function signContent(private_key: string, chain_id: string, level: number, merkle_root: string) {
    // Create signature.
    const signer = crypto.createSign('RSA-SHA256');
    signer.update(buildContent(chain_id, level, merkle_root));
    let sigString = signer.sign(private_key, 'hex');

    // Reformat signature / extract coordinates.
    const xlength = 2 * Number('0x' + sigString.slice(6, 8));
    sigString = sigString.slice(8);

    return [sigString.slice(0, xlength), sigString.slice(xlength + 4)];
}

function loadSecp256r1KeyPair(eth_private_key: string) {
    // Create curve object for key and signature generation.
    const prime256v1 = crypto.createECDH('prime256v1');
    prime256v1.setPrivateKey(Buffer.from(eth_private_key, 'hex'));
    const public_key = [
        '0x' + prime256v1.getPublicKey('hex').slice(2, 66),
        '0x' + prime256v1.getPublicKey('hex').slice(-64),
    ];
    // Reformat keys.
    const pemFormattedKeyPair = ecPem(prime256v1, 'prime256v1');

    return [public_key, pemFormattedKeyPair.encodePrivateKey()];
}

interface MonitorContext {
    tezos_sdk: TezosToolkit;
    chain_id: string;
    merkle_history_map: BigMapAbstraction;
    ibcf_tezos_state_contract: ContractAbstraction<any>;
    eth_private_key: string;
    validator_address: string;
}

class Monitor {
    constructor(private context: MonitorContext) {}

    public async run() {
        const storage = await this.context.ibcf_tezos_state_contract.storage<{
            merkle_history: BigMapAbstraction;
            merkle_history_indexes: any[];
        }>();

        for (const idx of storage.merkle_history_indexes) {
            const level = idx.toNumber();
            const merkle_tree = await storage.merkle_history.get<{
                root: string;
                signatures: MichelsonMap<string, any>;
            }>(level);

            let alreadySigned = false;
            for (const signer of merkle_tree?.signatures.keys() || []) {
                if (this.context.validator_address === signer) {
                    alreadySigned = true;
                }
            }

            if (!alreadySigned && merkle_tree?.root) {
                const [r, s] = signContent(
                    this.context.eth_private_key,
                    this.context.chain_id,
                    level,
                    merkle_tree.root,
                );
                await this.context.ibcf_tezos_state_contract.methods.submit_signature(level, r, s).send();
                console.log(`Signed merkle root '${merkle_tree.root}' generated at level ${level}.`);
            }
        }
    }
}

function getEnv() {
    const env = {
        TEZOS_RPC: process.env['TEZOS_RPC']!,
        IBCF_TEZOS_AGGREGATOR_ADDRESS: process.env['IBCF_TEZOS_AGGREGATOR_ADDRESS']!,
        TEZOS_PRIVATE_KEY: process.env['TEZOS_PRIVATE_KEY2']!,
        ETH_PRIVATE_KEY: process.env['ETH_PRIVATE_KEY']!,
    };
    // Validate environment variables
    Object.entries(env).forEach(([key, value]) => {
        if (!value) {
            console.log(`\nEnvironment variable ${key} is required!\n`);
            process.exit(1);
        }
    });
    return env;
}

export async function run_tezos_monitor() {
    const env = getEnv();
    // Tezos
    const tezos_sdk = new TezosToolkit(env.TEZOS_RPC);
    tezos_sdk.setProvider({ signer: await InMemorySigner.fromSecretKey(env.TEZOS_PRIVATE_KEY) });
    /// Client contract
    const ibcf_tezos_state_address = env.IBCF_TEZOS_AGGREGATOR_ADDRESS;
    const ibcf_tezos_state_contract = await tezos_sdk.contract.at(ibcf_tezos_state_address);

    const storage = await ibcf_tezos_state_contract.storage<{ merkle_history: BigMapAbstraction }>();

    const context: MonitorContext = {
        tezos_sdk,
        ibcf_tezos_state_contract,
        chain_id: (b58cdecode(await tezos_sdk.rpc.getChainId(), new Uint8Array([0x87, 0x82, 0x00])) as any).toString(
            'hex',
        ),
        merkle_history_map: storage.merkle_history,
        eth_private_key: loadSecp256r1KeyPair(env.ETH_PRIVATE_KEY)[1],
        validator_address: await tezos_sdk.signer.publicKeyHash(),
    };

    const monitor = new Monitor(context);
    // Start service
    while (1) {
        // Sleep 5 seconds before each check
        await new Promise((r) => setTimeout(r, 5000));

        try {
            await monitor.run();
        } catch (e) {
            console.error(e);
        }
    }
}
