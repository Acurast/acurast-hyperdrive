import { encodeExpr } from '@taquito/utils';
import { ContractAbstraction, TezosToolkit } from '@taquito/taquito';
import { OperationEntry } from '@taquito/rpc/dist/types/types';
import Web3 from 'web3';
import web3Utils from 'web3-utils';
import { Contract } from 'web3-eth-contract';
import { Transaction } from 'ethereumjs-tx';

import { ibfc_client_abi } from './abi';
import { pack_address, pack_nat } from './utils';
import constants from './constants';
import { isTransationContents } from './typing/guards';

interface MonitorContext {
    chain: string;
    tezos_sdk: TezosToolkit;
    latest_hash?: string;
    latest_level: number;
    big_map_id: string;
    web3_sdk: Web3;
    ibcf_eth_client_contract: Contract;
    ibcf_tezos_client_contract: ContractAbstraction<any>;
    ibcf_eth_client_address: string;
    ibcf_tezos_aggregator_contract: ContractAbstraction<any>;
    ibcf_tezos_aggregator_address: string;
    eth_caller_address: string;
    eth_private_key: Buffer;
    pending_tasks: Map<number, any>;
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
                        const tree: any = await context.tezos_sdk.rpc.getBigMapExpr(
                            context.big_map_id,
                            encodeExpr(pack_nat(context.latest_level)),
                        );
                        const merkle_root = tree['args'][1]['bytes'];
                        // Add pending action
                        context.pending_tasks.set(context.latest_level, {
                            merkle_root,
                            owner: pack_address(context.ibcf_tezos_client_contract.address),
                            key: (internal_op.parameters?.value as any)['args'][0]['bytes'],
                            value: (internal_op.parameters?.value as any)['args'][1]['bytes'],
                            signatures: [],
                        });
                    });
            }
        });
}

async function verifyPending(context: MonitorContext) {
    context.pending_tasks.forEach(async (v, level) => {
        const merkle_tree: any = await context.tezos_sdk.rpc.getBigMapExpr(
            context.big_map_id,
            encodeExpr(pack_nat(level)),
        );
        const signatures = merkle_tree['args'][3];
        if (signatures.length >= constants.min_signatures) {
            const proof = await context.ibcf_tezos_aggregator_contract.contractViews
                .get_proof({ key: v.key, owner: context.ibcf_tezos_client_contract.address, level: level })
                .executeView({ viewCaller: context.ibcf_tezos_client_contract.address });

            const signers = [];
            const signatures: any[] = [];
            for (const [k, { r, s }] of proof.signatures.entries()) {
                signers.push(pack_address(k));
                signatures.push(['0x' + r, '0x' + s]);
            }

            const method = context.ibcf_eth_client_contract.methods.mint(
                level,
                '0x' + proof.merkle_root,
                '0x' + v.key,
                '0x' + v.value,
                proof.proof,
                [context.eth_caller_address],
                signatures,
            );
            const gasEstimate = await method.estimateGas();
            context.web3_sdk.eth.getTransactionCount(context.eth_caller_address, (err, txCount) => {
                console.log(err);
                context.web3_sdk.eth.getGasPrice(function (err, gasPrice) {
                    console.log(err);

                    // Build the transaction
                    const txObject = {
                        from: context.eth_caller_address,
                        nonce: web3Utils.toHex(txCount),
                        to: context.ibcf_eth_client_address,
                        value: '0x0',
                        gas: web3Utils.toHex(gasEstimate),
                        gasPrice: web3Utils.toHex(gasPrice),
                        data: method.encodeABI(),
                    };

                    // Sign the transaction
                    const tx = new Transaction(txObject, { chain: context.chain });
                    tx.sign(context.eth_private_key);

                    // Broadcast the transaction
                    const raw = '0x' + tx.serialize().toString('hex');
                    const transaction = context.web3_sdk.eth.sendSignedTransaction(raw, (err, tx) => {
                        console.log(err, tx);
                        context.pending_tasks.delete(level);
                    });
                });
            });
        }
    });
}

async function monitor(context: MonitorContext) {
    const block = await (context.latest_level == 0
        ? context.tezos_sdk.rpc.getBlock()
        : context.tezos_sdk.rpc.getBlock({ block: String(context.latest_level + 1) }));

    // Block already verified, skip
    if (context.latest_hash == block.hash) {
        return;
    }
    context.latest_hash = block.hash;
    context.latest_level = block.header.level;

    const manager_operations = block.operations[3];
    console.log('Latest level', context.latest_level, context.latest_hash);
    await verifyLockOperations(context, manager_operations);
    await verifyPending(context);
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
    // Tezos
    const tezos_sdk = new TezosToolkit(env.TEZOS_RPC);
    /// Client contract
    const ibcf_tezos_client_address = env.IBCF_TEZOS_CLIENT_ADDRESS;
    const ibcf_tezos_client_contract = await tezos_sdk.contract.at(ibcf_tezos_client_address);
    /// Aggregator contract
    const ibcf_tezos_aggregator_address = env.IBCF_TEZOS_AGGREGATOR_ADDRESS;
    const ibcf_tezos_aggregator_contract = await tezos_sdk.contract.at(ibcf_tezos_aggregator_address);
    const storage: any = await ibcf_tezos_aggregator_contract.storage();

    const context: MonitorContext = {
        chain: env.ETH_CHAIN,
        tezos_sdk,
        web3_sdk,
        latest_hash: undefined,
        latest_level: 917385,
        big_map_id: storage['merkle_history'].id.toNumber(),
        ibcf_eth_client_contract: new web3_sdk.eth.Contract(ibfc_client_abi, env.IBCF_ETH_CLIENT_ADDRESS),
        ibcf_tezos_client_contract,
        ibcf_eth_client_address: env.IBCF_ETH_CLIENT_ADDRESS,
        ibcf_tezos_aggregator_contract,
        ibcf_tezos_aggregator_address,
        eth_caller_address: '0x836F1aBf07dbdb7F262D0A71067DADC421Fe3Df0',
        eth_private_key: Buffer.from(env.ETH_PRIVATE_KEY, 'hex'),
        pending_tasks: new Map(),
    };

    // Start service
    while (1) {
        // Sleep 5 seconds before each check
        await new Promise((r) => setTimeout(r, 5000));

        try {
            await monitor(context);
        } catch (e) {
            console.error(e);
        }
    }
})();
