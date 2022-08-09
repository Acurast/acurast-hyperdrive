import { ContractAbstraction, TezosToolkit } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';
import Web3 from 'web3';

interface MonitorContext {
    tezos_sdk: TezosToolkit;
    latest_block_number: number;
    min_signatures: number;
    web3_sdk: Web3;
    ibcf_eth_client_address: string;
    ibcf_tezos_validator_contract: ContractAbstraction<any>;
}

class EthMonitor {
    constructor(private context: MonitorContext) {}

    public async run() {
        const blockNumber = await this.context.web3_sdk.eth.getBlockNumber();
        if (blockNumber <= this.context.latest_block_number) {
            return;
        }

        const block = await this.context.web3_sdk.eth.getBlock(blockNumber);
        if (block) {
            const stateRoot = block.stateRoot;

            await this.context.ibcf_tezos_validator_contract.methods
                .submit_block_state_root(blockNumber, stateRoot.slice(2))
                .send();

            console.log('Latest confirmed level:', blockNumber);

            this.context.latest_block_number = blockNumber;
        }
    }
}

function getEnv() {
    const env = {
        ETH_RPC: process.env['ETH_RPC']!,
        TEZOS_RPC: process.env['TEZOS_RPC']!,
        IBCF_ETH_CLIENT_ADDRESS: process.env['IBCF_ETH_CLIENT_ADDRESS']!,
        IBCF_TEZOS_VALIDATOR_ADDRESS: process.env['IBCF_TEZOS_VALIDATOR_ADDRESS']!,
        MIN_SIGNATURES: Number(process.env['MIN_SIGNATURES']!),
        PRIVATE_KEY: process.env['TEZOS_PRIVATE_KEY']!,
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

export async function run_eth_monitor() {
    const env = getEnv();
    // Ethereum
    const web3_sdk = new Web3(env.ETH_RPC);
    // Tezos
    const tezos_sdk = new TezosToolkit(env.TEZOS_RPC);
    tezos_sdk.setProvider({ signer: await InMemorySigner.fromSecretKey(env.PRIVATE_KEY) });
    /// Client contract
    const ibcf_tezos_validator_contract = await tezos_sdk.contract.at(env.IBCF_TEZOS_VALIDATOR_ADDRESS);

    // Start from head block
    const latest_block_number = Number(process.env['LATEST_LEVEL']) || 0;

    const context: MonitorContext = {
        tezos_sdk,
        web3_sdk,
        latest_block_number,
        min_signatures: env.MIN_SIGNATURES,
        ibcf_eth_client_address: env.IBCF_ETH_CLIENT_ADDRESS,
        ibcf_tezos_validator_contract,
    };

    const monitor = new EthMonitor(context);

    // Start service
    while (1) {
        // Sleep 10 seconds before each check
        await new Promise((r) => setTimeout(r, 10000));

        try {
            monitor.run();
        } catch (e) {
            //console.error(e);
        }
    }
}
