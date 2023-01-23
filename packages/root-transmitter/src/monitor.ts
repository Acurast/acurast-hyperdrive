import { MichelsonMap, TezosToolkit, TransferParams } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';
import { BigNumber, ethers } from 'ethers';

import { Ethereum, Tezos } from 'ibcf-sdk';
import Logger from './logger';

interface MonitorContext {
    tezos_finality: number;
    tezos_finalize_snapshots: boolean;
    tezos_sdk: TezosToolkit;
    tezos_state: Tezos.Contracts.StateAggregator.Contract;
    tezos_validator: Tezos.Contracts.Validator.Contract;
    ethereum_signer: ethers.Wallet;
    ethereum_finality: number;
    evm_validator: Ethereum.Contracts.Validator.Contract;
    processor_tezos_address: string;
}

class Monitor {
    constructor(private context: MonitorContext) {}
    tezos_operations: TransferParams[] = [];
    latest_tezos_snapshot = 0;

    public async run() {
        this.tezos_operations = [];

        // Transmit new ethereum block states to Tezos
        await this.ethereumToTezos();

        const stateAggregatorStorage = await this.context.tezos_state.getStorage();
        const tezosBlockLevel = (await this.context.tezos_sdk.rpc.getBlockHeader()).level;

        // Snapshot state if it can be done.
        await this.snapshotIfPossible(stateAggregatorStorage, tezosBlockLevel);

        const ethExpectedSnapshot = await this.context.evm_validator.getCurrentSnapshot();

        if (
            stateAggregatorStorage.snapshot_counter.gte(ethExpectedSnapshot) &&
            ethExpectedSnapshot.isGreaterThan(this.latest_tezos_snapshot)
        ) {
            // Make sure at least `this.context.tezos_finality` blocks have been confirmed
            const snapshot_level = (
                await stateAggregatorStorage.snapshot_level.get<BigNumber>(ethExpectedSnapshot)
            )?.toNumber();
            if (snapshot_level && tezosBlockLevel - snapshot_level > this.context.tezos_finality) {
                // Get snapshot submissions
                const ethCurrentSnapshotSubmissions = await this.context.evm_validator.getCurrentSnapshotSubmissions();

                Logger.debug(
                    '[ETHEREUM]',
                    'Confirming snapshot:',
                    `${ethExpectedSnapshot} of ${stateAggregatorStorage.snapshot_counter}`,
                    `\n\tSubmissions:`,
                    ethCurrentSnapshotSubmissions,
                );

                if (!ethCurrentSnapshotSubmissions.includes(this.context.ethereum_signer.address)) {
                    const storageAtSnapshot = await this.context.tezos_state.getStorage(String(snapshot_level));

                    const result = await this.context.evm_validator.submitStateRoot(
                        ethExpectedSnapshot,
                        '0x' + storageAtSnapshot.merkle_tree.root,
                    );

                    // Wait for the operation to be included in at least `ethereum_finality` blocks.
                    await result.wait(this.context.ethereum_finality);

                    Logger.info(
                        '[Tezos->ETHEREUM]',
                        `Submit state root "${storageAtSnapshot.merkle_tree.root}" for snapshot ${ethExpectedSnapshot}.`,
                        `\n\tOperation hash: ${result.hash}`,
                    );

                    this.latest_tezos_snapshot = ethExpectedSnapshot.toNumber();
                }
            }
        }

        // Commit operations
        await this.commitTezosOperations();
    }

    /**
     * Transmit Ethereum block states to Tezos
     */
    private async ethereumToTezos() {
        const validator_storage = await this.context.tezos_validator.getStorage();

        const latest_block = await this.context.ethereum_signer.provider.getBlockNumber();
        const current_snapshot = validator_storage.current_snapshot.toNumber();
        if (latest_block < current_snapshot) {
            return;
        }

        // Get endorsers
        const snapshot_submissions = await validator_storage.state_root.get<MichelsonMap<string, string>>(
            current_snapshot,
        );
        const endorsers: string[] = [];
        const keys = snapshot_submissions?.keys() || [];
        for (const key of keys) {
            endorsers.push(key);
        }

        Logger.debug('[TEZOS]', 'Confirming block:', current_snapshot, `\n\tSubmissions:`, endorsers);

        if (!endorsers.includes(this.context.processor_tezos_address)) {
            const provider = this.context.ethereum_signer.provider as ethers.providers.JsonRpcProvider;
            const rawBlock = await provider.send('eth_getBlockByNumber', [
                ethers.utils.hexValue(current_snapshot),
                true,
            ]);
            const state_root = provider.formatter.hash(rawBlock.stateRoot);

            Logger.info('[ETHEREUM->TEZOS]', `Submit state root "${state_root}" for block:`, current_snapshot);

            this.tezos_operations.push(
                (
                    await this.context.tezos_validator.submitBlockStateRoot(current_snapshot, state_root)
                ).toTransferParams(),
            );
        }
    }

    private async snapshotIfPossible(
        storage: Tezos.Contracts.StateAggregator.StateAggregatorStorage,
        blockLevel: number,
    ) {
        if (
            storage.snapshot_start_level.plus(storage.config.snapshot_duration).lt(blockLevel) &&
            storage.merkle_tree.root
        ) {
            Logger.info('[TEZOS]', `Finalizing snapshot:`, storage.snapshot_counter.toNumber());

            this.tezos_operations.push((await this.context.tezos_state.snapshot()).toTransferParams());
        }
    }

    private async commitTezosOperations() {
        if (this.tezos_operations.length > 0) {
            const op = await this.tezos_operations
                .reduce((batch, op) => batch.withTransfer(op), this.context.tezos_sdk.contract.batch())
                .send();

            // Wait for operation to be included.
            await op.confirmation(this.context.tezos_finality);
        }
    }
}
export interface Env {
    TEZOS_RPC: string;
    TEZOS_FINALITY: number;
    TEZOS_FINALIZE_SNAPSHOTS: boolean;
    TEZOS_STATE_ADDRESS: string;
    TEZOS_VALIDATOR_ADDRESS: string;
    TEZOS_PRIVATE_KEY: string;
    ETHEREUM_RPC: string;
    ETHEREUM_FINALITY: number;
    ETHEREUM_PRIVATE_KEY: string;
    EVM_VALIDATOR_ADDRESS: string;
}
export async function run_monitor(env: Env) {
    // Tezos
    const tezos_sdk = new TezosToolkit(env.TEZOS_RPC);
    tezos_sdk.setProvider({ signer: await InMemorySigner.fromSecretKey(env.TEZOS_PRIVATE_KEY) });
    // Ethereum
    const provider = new ethers.providers.JsonRpcProvider(env.ETHEREUM_RPC);
    const ethereum_signer = new ethers.Wallet(env.ETHEREUM_PRIVATE_KEY, provider);

    const context: MonitorContext = {
        tezos_sdk,
        tezos_finality: env.TEZOS_FINALITY,
        tezos_finalize_snapshots: env.TEZOS_FINALIZE_SNAPSHOTS,
        ethereum_finality: env.ETHEREUM_FINALITY,
        ethereum_signer,
        tezos_state: new Tezos.Contracts.StateAggregator.Contract(tezos_sdk, env.TEZOS_STATE_ADDRESS),
        tezos_validator: new Tezos.Contracts.Validator.Contract(tezos_sdk, env.TEZOS_VALIDATOR_ADDRESS),
        evm_validator: new Ethereum.Contracts.Validator.Contract(ethereum_signer, env.EVM_VALIDATOR_ADDRESS),
        processor_tezos_address: await tezos_sdk.signer.publicKeyHash(),
    };

    const monitor = new Monitor(context);
    // Start service
    while (1) {
        try {
            await monitor.run();
        } catch (e) {
            console.error(e);
        }
    }
}
