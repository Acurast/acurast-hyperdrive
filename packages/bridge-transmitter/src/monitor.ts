import { TezosToolkit, TransferParams } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';
import { BigNumber, ethers } from 'ethers';

import { Ethereum, Tezos } from 'ibcf-sdk';
import Logger from './logger';

interface MonitorContext {
    tezos_finality: number;
    tezos_sdk: TezosToolkit;
    tezos_bridge_address: string;
    tezos_bridge: Tezos.Contracts.Bridge.Contract;
    tezos_state: Tezos.Contracts.StateAggregator.Contract;
    tezos_latest_unwrap_nonce: number;
    ethereum_signer: ethers.Wallet;
    ethereum_finality: number;
    evm_bridge_address: string;
    evm_bridge: Ethereum.Contracts.Bridge.Contract;
    processor_address: string;
}

class Monitor {
    constructor(private context: MonitorContext) {}
    tezos_operations: TransferParams[] = [];

    public async run() {
        this.tezos_operations = [];

        const tezosBridgeStorage = await this.context.tezos_bridge.getStorage();

        // Wrap assets from Ethereum to Tezos
        await this.ethereumToTezos(tezosBridgeStorage);

        // Unwrap assets from Tezos to Ethereum
        await this.tezosToEthereum(tezosBridgeStorage);

        // Commit Tezos operations
        await this.commitTezosOperations();
    }

    /**
     * Unwrap assets from Tezos to Ethereum
     */
    private async tezosToEthereum(bridgeStorage: Tezos.Contracts.Bridge.BridgeStorage) {
        // For every new unwrap
        let latest = this.context.tezos_latest_unwrap_nonce;
        for (; bridgeStorage.nonce.gte(latest); latest++) {
            try {
                const wasProcessed = await this.context.evm_bridge.unwrapProcessed(latest);
                const unwrap: any = await bridgeStorage.registry.get(latest);
                if (!wasProcessed && unwrap) {
                    const stateStorage = await this.context.tezos_state.getStorage(unwrap.level);
                    const snapshotLevel = await stateStorage.snapshot_level.get<BigNumber>(
                        stateStorage.snapshot_counter.plus(1),
                    );
                    if (snapshotLevel) {
                        const key = this.context.tezos_bridge.computeUnwrapProofKey(latest);
                        const proof = await this.context.tezos_state.getProof(
                            this.context.tezos_bridge_address,
                            key,
                            snapshotLevel.toNumber(),
                        );
                        const result = await this.context.evm_bridge.unwrap(
                            proof.snapshot,
                            proof.key,
                            proof.value,
                            proof.path,
                        );

                        // Wait for the operation to be included in at least `ethereum_finality` blocks.
                        await result.wait(this.context.ethereum_finality);
                    }
                }
            } catch (e: any) {
                Logger.debug(e.message);
            }
        }
    }

    /**
     * Wrap assets from Ethereum to Tezos
     */
    private async ethereumToTezos(bridgeStorage: Tezos.Contracts.Bridge.BridgeStorage) {
        try {
            const latestWraps = await this.context.evm_bridge.getWraps();

            const tezosValidator = new Tezos.Contracts.Validator.Contract(
                this.context.tezos_sdk,
                bridgeStorage.proof_validator,
            );
            const validatorStorage = await tezosValidator.getStorage();

            if (validatorStorage.history.length > 0) {
                const blockNumber = validatorStorage.history.pop()!.toNumber();

                for (const wrap of latestWraps) {
                    const nonce = wrap.nonce.toString(16).padStart(64, '0');
                    if (!(await bridgeStorage.wrap_nonce.get(nonce))) {
                        // Can be processed
                        const proof = await this.context.evm_bridge.generateWrapProof(nonce, blockNumber);
                        const args = {
                            account_proof_rlp: proof.account_proof_rlp,
                            amount_proof_rlp: proof.amount_proof_rlp,
                            destination_proof_rlp: proof.destination_proof_rlp,
                            block_number: blockNumber.toString(),
                            nonce: '0x' + nonce,
                        };

                        Logger.info(
                            '[ETHEREUM->TEZOS]',
                            `Submit wrap operation "${wrap.nonce.toString()}":\n\tDestination: ${
                                wrap.address
                            }\n\tAmount: ${wrap.amount.toString()}`,
                        );

                        this.tezos_operations.push((await this.context.tezos_bridge.wrap(args)).toTransferParams());
                    }
                }
            }
        } catch (e) {
            Logger.debug(e);
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
    TEZOS_STATE_ADDRESS: string;
    TEZOS_PRIVATE_KEY: string;
    TEZOS_BRIDGE_ADDRESS: string;
    TEZOS_LATEST_UNWRAP_NONCE: number;
    ETHEREUM_RPC: string;
    ETHEREUM_FINALITY: number;
    ETHEREUM_PRIVATE_KEY: string;
    EVM_BRIDGE_ADDRESS: string;
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
        tezos_latest_unwrap_nonce: env.TEZOS_LATEST_UNWRAP_NONCE,
        ethereum_finality: env.ETHEREUM_FINALITY,
        ethereum_signer,
        tezos_bridge_address: env.TEZOS_BRIDGE_ADDRESS,
        tezos_bridge: new Tezos.Contracts.Bridge.Contract(tezos_sdk, env.TEZOS_BRIDGE_ADDRESS),
        tezos_state: new Tezos.Contracts.StateAggregator.Contract(tezos_sdk, env.TEZOS_STATE_ADDRESS),
        evm_bridge: new Ethereum.Contracts.Bridge.Contract(ethereum_signer, env.EVM_BRIDGE_ADDRESS),
        evm_bridge_address: env.EVM_BRIDGE_ADDRESS,
        processor_address: await tezos_sdk.signer.publicKeyHash(),
    };

    const monitor = new Monitor(context);
    // Start service
    while (1) {
        try {
            await monitor.run();
        } catch (e) {
            Logger.error(e);
        }
    }
}
