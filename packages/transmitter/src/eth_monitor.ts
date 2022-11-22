import { ContractAbstraction, TezosToolkit } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';
import Web3 from 'web3';

interface MonitorContext {
    tezos_sdk: TezosToolkit;
    from_block: number;
    web3_sdk: Web3;
    ibcf_tezos_validator_contract: ContractAbstraction<any>;
}

class EthMonitor {
    constructor(private context: MonitorContext) {}

    public async run() {
        const currentBlockNumber = await this.context.web3_sdk.eth.getBlockNumber();
        if (this.context.from_block > currentBlockNumber) {
            return;
        }

        const block = await this.context.web3_sdk.eth.getBlock(this.context.from_block);
        if (block) {
            const stateRoot = block.stateRoot;

            await this.context.ibcf_tezos_validator_contract.methods
                .submit_block_state_root(block.number, stateRoot.slice(2))
                .send();

            console.log('Latest confirmed level:', block.number);

            this.context.from_block += 1;
        }
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

    const from_block = Number(process.env['FROM_BLOCK']) || 0;

    const context: MonitorContext = {
        tezos_sdk,
        web3_sdk,
        from_block,
        ibcf_tezos_validator_contract,
    };

    const monitor = new EthMonitor(context);

    // Start service
    while (1) {
        try {
            await monitor.run();
        } catch (e) {
            //console.error(e);
        }
    }
}
