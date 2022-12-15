import { ContractAbstraction, TezosToolkit } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';
import Web3 from 'web3';
import Logger from './logger';

interface MonitorContext {
    tezos_sdk: TezosToolkit;
    latest_block_hash?: string;
    web3_sdk: Web3;
    ibcf_tezos_validator_contract: ContractAbstraction<any>;
}

class EthMonitor {
    constructor(private context: MonitorContext) {}

    public async run(): Promise<void> {
        const latestBlock = await this.context.web3_sdk.eth.getBlock('latest');
        if (this.context.latest_block_hash == latestBlock.hash) {
            return; // already processed
        }

        // Submit block state root
        await (
            await this.context.ibcf_tezos_validator_contract.methods
                .submit_block_state_root(latestBlock.stateRoot)
                .send()
        ).confirmation(1);

        this.context.latest_block_hash = latestBlock.hash;

        Logger.info('Processed block', latestBlock.number, 'with hash', this.context.latest_block_hash);
    }
}

function getEnv() {
    const env = {
        ETH_RPC: process.env['ETH_RPC']!,
        TEZOS_RPC: process.env['TEZOS_RPC']!,
        IBCF_TEZOS_VALIDATOR_ADDRESS: process.env['IBCF_TEZOS_VALIDATOR_ADDRESS']!,
        PRIVATE_KEY: process.env['TEZOS_PRIVATE_KEY']!,
    };
    // Validate environment variables
    Object.entries(env).forEach(([key, value]) => {
        if (!value) {
            Logger.error(`\nEnvironment variable ${key} is required!\n`);
            process.exit(1);
        }
    });
    return env;
}

export async function run_eth_monitor() {
    const env = getEnv();
    // Ethereum
    const web3_sdk = new Web3(env.ETH_RPC);
    // Tezos
    const tezos_sdk = new TezosToolkit(env.TEZOS_RPC);
    tezos_sdk.setProvider({ signer: await InMemorySigner.fromSecretKey(env.PRIVATE_KEY) });
    /// Client contract
    const ibcf_tezos_validator_contract = await tezos_sdk.contract.at(env.IBCF_TEZOS_VALIDATOR_ADDRESS);

    const context: MonitorContext = {
        tezos_sdk,
        web3_sdk,
        ibcf_tezos_validator_contract,
    };

    const monitor = new EthMonitor(context);

    // Run service
    while (1) {
        try {
            await monitor.run();
        } catch (e) {
            console.error(e);
        }
    }
}
