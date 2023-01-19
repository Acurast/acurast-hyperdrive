"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.run_monitor = void 0;
const taquito_1 = require("@taquito/taquito");
const signer_1 = require("@taquito/signer");
const ethers_1 = require("ethers");
const sdk_1 = require("@ibcf/sdk");
const logger_1 = __importDefault(require("./logger"));
class Monitor {
    constructor(context) {
        this.context = context;
        this.tezos_operations = [];
    }
    run() {
        var _a;
        return __awaiter(this, void 0, void 0, function* () {
            this.tezos_operations = [];
            // Transmit new ethereum block states to Tezos
            yield this.ethereumToTezos();
            const state_aggregator_storage = yield this.context.tezos_state.getStorage();
            const tezosBlockLevel = (yield this.context.tezos_sdk.rpc.getBlockHeader()).level;
            // Snapshot state if it can be done.
            yield this.snapshotIfPossible(state_aggregator_storage, tezosBlockLevel);
            const eth_current_snapshot = yield this.context.evm_validator.getCurrentSnapshot();
            if (state_aggregator_storage.snapshot_counter.gte(eth_current_snapshot)) {
                // Make sure at least `this.context.tezos_finality` blocks have been confirmed
                const snapshot_level = (_a = (yield state_aggregator_storage.snapshot_level.get(eth_current_snapshot))) === null || _a === void 0 ? void 0 : _a.toNumber();
                if (snapshot_level && tezosBlockLevel - snapshot_level > this.context.tezos_finality) {
                    // Get snapshot submissions
                    const eth_current_snapshot_submissions = yield this.context.evm_validator.getCurrentSnapshotSubmissions();
                    logger_1.default.debug('[ETHEREUM]', 'Confirming snapshot:', `${eth_current_snapshot} of ${state_aggregator_storage.snapshot_counter}`, `\n\tSubmissions:`, eth_current_snapshot_submissions);
                    if (!eth_current_snapshot_submissions.includes(this.context.ethereum_signer.address)) {
                        const storage_at_snapshot = yield this.context.tezos_state.getStorage(String(snapshot_level));
                        const result = yield this.context.evm_validator.submitStateRoot(eth_current_snapshot, '0x' + storage_at_snapshot.merkle_tree.root);
                        // Wait for the operation to be included in at least `ethereum_finality` blocks.
                        yield result.wait(this.context.ethereum_finality);
                        logger_1.default.info('[Tezos->ETHEREUM]', `Submit state root "${storage_at_snapshot.merkle_tree.root}" for snapshot ${eth_current_snapshot}.`, `\n\tOperation hash: ${result.hash}`);
                    }
                }
            }
            // Commit operations
            yield this.commitTezosOperations();
        });
    }
    /**
     * Transmit Ethereum block states to Tezos
     */
    ethereumToTezos() {
        return __awaiter(this, void 0, void 0, function* () {
            const validator_storage = yield this.context.tezos_validator.getStorage();
            const latest_block = yield this.context.ethereum_signer.provider.getBlockNumber();
            const current_snapshot = validator_storage.current_snapshot.toNumber();
            if (latest_block < current_snapshot) {
                return;
            }
            // Get endorsers
            const snapshot_submissions = yield validator_storage.state_root.get(current_snapshot);
            const endorsers = [];
            const keys = (snapshot_submissions === null || snapshot_submissions === void 0 ? void 0 : snapshot_submissions.keys()) || [];
            for (const key of keys) {
                endorsers.push(key);
            }
            logger_1.default.debug('[Tezos]', 'Confirming block:', current_snapshot, `\n\tSubmissions:`, endorsers);
            if (!endorsers.includes(this.context.processor_tezos_address)) {
                const provider = this.context.ethereum_signer.provider;
                const rawBlock = yield provider.send('eth_getBlockByNumber', [
                    ethers_1.ethers.utils.hexValue(current_snapshot),
                    true,
                ]);
                const state_root = provider.formatter.hash(rawBlock.stateRoot);
                logger_1.default.info('[ETHEREUM->TEZOS]', `Submit state root "${state_root}" for block:`, current_snapshot);
                this.tezos_operations.push((yield this.context.tezos_validator.submit_block_state_root(current_snapshot, state_root)).toTransferParams());
            }
        });
    }
    snapshotIfPossible(storage, blockLevel) {
        return __awaiter(this, void 0, void 0, function* () {
            if (storage.snapshot_start_level.plus(storage.config.snapshot_duration).lt(blockLevel) &&
                storage.merkle_tree.root) {
                logger_1.default.info('[TEZOS]', `Finalizing snapshot:`, storage.snapshot_counter.toNumber());
                this.tezos_operations.push((yield this.context.tezos_state.snapshot()).toTransferParams());
            }
        });
    }
    commitTezosOperations() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.tezos_operations.length > 0) {
                const op = yield this.tezos_operations
                    .reduce((batch, op) => batch.withTransfer(op), this.context.tezos_sdk.contract.batch())
                    .send();
                // Wait for operation to be included.
                yield op.confirmation(this.context.tezos_finality);
            }
        });
    }
}
function run_monitor(env) {
    return __awaiter(this, void 0, void 0, function* () {
        // Tezos
        const tezos_sdk = new taquito_1.TezosToolkit(env.TEZOS_RPC);
        tezos_sdk.setProvider({ signer: yield signer_1.InMemorySigner.fromSecretKey(env.TEZOS_PRIVATE_KEY) });
        // Ethereum
        const provider = new ethers_1.ethers.providers.JsonRpcProvider(env.ETHEREUM_RPC);
        const ethereum_signer = new ethers_1.ethers.Wallet(env.ETHEREUM_PRIVATE_KEY, provider);
        const context = {
            tezos_sdk,
            tezos_finality: env.TEZOS_FINALITY,
            tezos_finalize_snapshots: env.TEZOS_FINALIZE_SNAPSHOTS,
            ethereum_finality: env.ETHEREUM_FINALITY,
            ethereum_signer,
            tezos_state: new sdk_1.Tezos.Contracts.StateAggregator.Contract(tezos_sdk, env.TEZOS_STATE_ADDRESS),
            tezos_validator: new sdk_1.Tezos.Contracts.Validator.Contract(tezos_sdk, env.TEZOS_VALIDATOR_ADDRESS),
            evm_validator: new sdk_1.Ethereum.Contracts.Validator.Contract(ethereum_signer, env.EVM_VALIDATOR_ADDRESS),
            processor_tezos_address: yield tezos_sdk.signer.publicKeyHash(),
        };
        const monitor = new Monitor(context);
        // Start service
        while (1) {
            try {
                yield monitor.run();
            }
            catch (e) {
                console.error(e);
            }
        }
    });
}
exports.run_monitor = run_monitor;
