import { encodeExpr } from '@taquito/utils';
import { ContractAbstraction, TezosToolkit } from '@taquito/taquito';
import { OperationEntry } from '@taquito/rpc/dist/types/types';
import Web3 from 'web3';
import web3Utils from 'web3-utils';
import { Contract } from 'web3-eth-contract';
import { Transaction } from '@ethereumjs/tx';
import { privateToAddress } from '@ethereumjs/util';
import Common from '@ethereumjs/common';

import { ibfc_client_abi } from './abi';
import { pack_address, pack_nat } from './utils';
import constants from './constants';
import { isTransationContents } from './typing/guards';

interface Task {
    owner: string;
    key: string;
    value: string;
}

interface MonitorContext {
    chain: string;
    tezos_sdk: TezosToolkit;
    latest_hash?: string;
    latest_level: number;
    min_signatures: number;
    big_map_id: string;
    web3_sdk: Web3;
    ibcf_eth_client_contract: Contract;
    ibcf_eth_client_address: string;
    ibcf_tezos_client_contract: ContractAbstraction<any>;
    ibcf_tezos_aggregator_contract: ContractAbstraction<any>;
    eth_caller_address: string;
    eth_private_key: Buffer;
    pending_tasks: Map<number, Task>;
}

/**
 * Inspect every transaction targetting a given entrypoint of a given address and extract the actions that need to be performed.
 *
 * @param context
 * @param operations
 */
async function verifyLockOperations(context: MonitorContext, operations: OperationEntry[]) {
    operations
        .flatMap(({ contents }) => contents)
        .filter(isTransationContents)
        .filter(
            ({ destination, parameters }) =>
                destination === context.ibcf_tezos_client_contract.address &&
                parameters?.entrypoint === constants.ibcf_client_entrypoint,
        )
        .forEach((op) => {
            const status = op.metadata.operation_result.status;
            const internal_operation_results = op.metadata.internal_operation_results || [];
            if (status === 'applied') {
                internal_operation_results
                    .filter(
                        ({ destination, parameters }) =>
                            destination === context.ibcf_tezos_aggregator_contract.address &&
                            parameters?.entrypoint === constants.ibcf_aggregator_entrypoint,
                    )
                    .forEach(async (internal_op) => {
                        // Add pending action
                        context.pending_tasks.set(context.latest_level, {
                            owner: pack_address(context.ibcf_tezos_client_contract.address),
                            key: (internal_op.parameters?.value as any)['args'][0]['bytes'],
                            value: (internal_op.parameters?.value as any)['args'][1]['bytes'],
                        });
                    });
            }
        });
}

/**
 * Verify pending tasks (TODO: Support bulk operations)
 *
 * @param context
 */
async function verifyPendingTasks(context: MonitorContext) {
    for (const [level, task] of context.pending_tasks.entries()) {
        const merkle_tree: any = await context.tezos_sdk.rpc.getBigMapExpr(
            context.big_map_id,
            encodeExpr(pack_nat(level)),
        );
        const signatures = merkle_tree['args'][3];
        if (signatures.length >= context.min_signatures) {
            const proof = await context.ibcf_tezos_aggregator_contract.contractViews
                .get_proof({ key: task.key, owner: context.ibcf_tezos_client_contract.address, level: level })
                .executeView({ viewCaller: context.ibcf_tezos_client_contract.address });

            const signers = [];
            const signatures: string[][] = [];
            for (const [k, { r, s }] of proof.signatures.entries()) {
                signers.push(pack_address(k));
                signatures.push(['0x' + r, '0x' + s]);
            }

            const method = context.ibcf_eth_client_contract.methods.mint(
                level,
                '0x' + proof.merkle_root,
                '0x' + task.key,
                '0x' + task.value,
                proof.proof,
                [context.eth_caller_address],
                signatures,
            );
            const gasEstimate = await method.estimateGas();
            const counter = await context.web3_sdk.eth.getTransactionCount(context.eth_caller_address);
            const gasPrice = await context.web3_sdk.eth.getGasPrice();

            // Build the transaction
            const txObject = {
                from: context.eth_caller_address,
                nonce: web3Utils.toHex(counter),
                to: context.ibcf_eth_client_address,
                value: '0x0',
                gasLimit: web3Utils.toHex(gasEstimate),
                gasPrice: web3Utils.toHex(gasPrice),
                data: method.encodeABI(),
            };

            // Sign the transaction
            const common = new Common({ chain: Number(context.chain) });
            const tx = Transaction.fromTxData(txObject, { common });

            // Broadcast the transaction
            const raw = '0x' + tx.sign(context.eth_private_key).serialize().toString('hex');
            const transaction = await context.web3_sdk.eth.sendSignedTransaction(raw);
            console.log('Submitted operation:', transaction.transactionHash);
            console.log({
                level,
                merkle_root: '0x' + proof.merkle_root,
                key: '0x' + task.key,
                value: '0x' + task.value,
                proof: proof.proof,
                signers: [context.eth_caller_address],
                signatures,
            });
            // Remove completed task
            context.pending_tasks.delete(level);
        }
    }
}

async function monitor(context: MonitorContext) {
    const headBlockHeader = await context.tezos_sdk.rpc.getBlockHeader();
    if (context.latest_level >= headBlockHeader.level - 2) {
        // Block is not final yet
        return;
    }
    const block = await context.tezos_sdk.rpc.getBlock({ block: String(context.latest_level + 1) });
    context.latest_hash = block.hash;
    context.latest_level = block.header.level;

    console.log('Latest confirmed level:', context.latest_level, context.latest_hash);

    const manager_operations = block.operations[3];
    await verifyLockOperations(context, manager_operations);
    await verifyPendingTasks(context);
}

function getEnv() {
    const env = {
        ETH_RPC: process.env['ETH_RPC']!,
        TEZOS_RPC: process.env['TEZOS_RPC']!,
        IBCF_ETH_CLIENT_ADDRESS: process.env['IBCF_ETH_CLIENT_ADDRESS']!,
        IBCF_TEZOS_CLIENT_ADDRESS: process.env['IBCF_TEZOS_CLIENT_ADDRESS']!,
        IBCF_TEZOS_AGGREGATOR_ADDRESS: process.env['IBCF_TEZOS_AGGREGATOR_ADDRESS']!,
        ETH_CHAIN: process.env['ETH_CHAIN']!,
        ETH_PRIVATE_KEY: process.env['ETH_PRIVATE_KEY']!,
        MIN_SIGNATURES: Number(process.env['MIN_SIGNATURES']!),
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

(async () => {
    const env = getEnv();
    // Ethereum
    const web3_sdk = new Web3(env.ETH_RPC);
    const eth_private_key = Buffer.from(env.ETH_PRIVATE_KEY, 'hex');
    // Tezos
    const tezos_sdk = new TezosToolkit(env.TEZOS_RPC);
    /// Client contract
    const ibcf_tezos_client_address = env.IBCF_TEZOS_CLIENT_ADDRESS;
    const ibcf_tezos_client_contract = await tezos_sdk.contract.at(ibcf_tezos_client_address);
    /// Aggregator contract
    const ibcf_tezos_aggregator_address = env.IBCF_TEZOS_AGGREGATOR_ADDRESS;
    const ibcf_tezos_aggregator_contract = await tezos_sdk.contract.at(ibcf_tezos_aggregator_address);
    const storage: any = await ibcf_tezos_aggregator_contract.storage();

    // Start from head block
    const latest_level = Number(process.env['LATEST_LEVEL']) || (await tezos_sdk.rpc.getBlock()).header.level;

    const context: MonitorContext = {
        chain: env.ETH_CHAIN,
        tezos_sdk,
        web3_sdk,
        latest_level,
        latest_hash: undefined,
        min_signatures: env.MIN_SIGNATURES,
        big_map_id: storage['merkle_history'].id.toNumber(),
        ibcf_eth_client_contract: new web3_sdk.eth.Contract(ibfc_client_abi, env.IBCF_ETH_CLIENT_ADDRESS),
        ibcf_eth_client_address: env.IBCF_ETH_CLIENT_ADDRESS,
        ibcf_tezos_client_contract,
        ibcf_tezos_aggregator_contract,
        eth_caller_address: privateToAddress(eth_private_key).toString('hex'),
        eth_private_key,
        pending_tasks: new Map(),
    };

    // Start service
    while (1) {
        // Sleep 5 seconds before each check
        await new Promise((r) => setTimeout(r, 5000));

        try {
            await monitor(context);
        } catch (e) {
            if (process.env['DEBUG'] === 'true') {
                console.error(e);
            }
        }
    }
})();
