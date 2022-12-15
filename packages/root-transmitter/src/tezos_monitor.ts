import { TezosToolkit } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';
import { BigNumber, ethers } from 'ethers';

import { Ethereum, Tezos } from '@ibcf/sdk';
import Logger from './logger';

interface MonitorContext {
    ethereum_signer: ethers.Wallet;
    tezos_finality: number;
    ethereum_finality: number;
    tezos_sdk: TezosToolkit;
    tezos_state_address: string;
    evm_validator_address: string;
    validator_address: string;
}

class Monitor {
    constructor(private context: MonitorContext) {}

    public async run() {
        const tezosBlockLevel = (await this.context.tezos_sdk.rpc.getBlockHeader()).level;

        const state_aggregator_storage = await Tezos.Contracts.StateAggregator.getStorage(
            this.context.tezos_sdk,
            this.context.tezos_state_address,
        );
        this.snapshotIfPossible(state_aggregator_storage, tezosBlockLevel);

        const eth_current_snapshot = await Ethereum.Contracts.Validator.getCurrentSnapshot(
            this.context.ethereum_signer.provider,
            this.context.evm_validator_address,
        );

        if (state_aggregator_storage.snapshot_counter.gte(eth_current_snapshot)) {
            // Make sure at least `this.context.tezos_finality` blocks have been confirmed
            const snapshot_level = (
                await state_aggregator_storage.snapshot_level.get<BigNumber>(eth_current_snapshot)
            )?.toNumber();
            if (snapshot_level && tezosBlockLevel - snapshot_level > this.context.tezos_finality) {
                // Get snapshot submissions
                const eth_current_snapshot_submissions =
                    await Ethereum.Contracts.Validator.getCurrentSnapshotSubmissions(
                        this.context.ethereum_signer.provider,
                        this.context.evm_validator_address,
                    );

                Logger.debug(
                    'Confirming snapshot:',
                    `${eth_current_snapshot} of ${state_aggregator_storage.snapshot_counter}`,
                    `\n\tSubmissions: [${eth_current_snapshot_submissions.length}]`,
                );

                if (!eth_current_snapshot_submissions.includes(this.context.validator_address)) {
                    const storage_at_snapshot = await Tezos.Contracts.StateAggregator.getStorage(
                        this.context.tezos_sdk,
                        this.context.tezos_state_address,
                        String(snapshot_level),
                    );

                    const result = await Ethereum.Contracts.Validator.submitStateRoot(
                        this.context.ethereum_signer,
                        this.context.evm_validator_address,
                        eth_current_snapshot,
                        '0x' + storage_at_snapshot.merkle_tree.root,
                    );

                    // Wait for the operation to be included in at least 2 blocks.
                    await result.wait(this.context.ethereum_finality);

                    Logger.info(
                        `Submitted state root "${state_aggregator_storage.merkle_tree.root}" for snapshot ${eth_current_snapshot}.`,
                        `\n\tOperation kash: ${result.hash}`,
                    );
                }
            }
        }
    }

    public async snapshotIfPossible(
        storage: Tezos.Contracts.StateAggregator.StateAggregatorStorage,
        blockLevel: number,
    ) {
        if (storage.snapshot_start_level.plus(storage.config.snapshot_duration).gte(blockLevel)) {
            console.log(storage.merkle_tree.states);
        }
    }
}

function getEnv() {
    const env = {
        TEZOS_RPC: process.env['TEZOS_RPC']!,
        TEZOS_FINALITY: Number(process.env['TEZOS_FINALITY']!),
        TEZOS_AGGREGATOR_ADDRESS: process.env['TEZOS_AGGREGATOR_ADDRESS']!,
        TEZOS_PRIVATE_KEY: process.env['TEZOS_PRIVATE_KEY2']!,
        ETHEREUM_RPC: process.env['ETHEREUM_RPC']!,
        ETHEREUM_FINALITY: Number(process.env['ETHEREUM_FINALITY']!),
        ETH_PRIVATE_KEY: process.env['ETHEREUM_PRIVATE_KEY']!,
        EVM_VALIDATOR_ADDRESS: process.env['EVM_VALIDATOR_ADDRESS']!,
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
    // Ethereum
    const provider = new ethers.providers.JsonRpcProvider(env.ETHEREUM_RPC);
    const ethereum_signer = new ethers.Wallet(env.ETH_PRIVATE_KEY, provider);

    const context: MonitorContext = {
        tezos_sdk,
        tezos_finality: env.TEZOS_FINALITY,
        ethereum_finality: env.ETHEREUM_FINALITY,
        ethereum_signer,
        tezos_state_address: env.TEZOS_AGGREGATOR_ADDRESS,
        evm_validator_address: env.EVM_VALIDATOR_ADDRESS,
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
