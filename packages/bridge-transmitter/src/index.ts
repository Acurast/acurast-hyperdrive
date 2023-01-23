import Logger from './logger';
import { Env, run_monitor } from './monitor';

function getEnv(): Env {
    const env = {
        TEZOS_RPC: process.env['TEZOS_RPC']!,
        TEZOS_FINALITY: Number(process.env['TEZOS_FINALITY']!),
        TEZOS_STATE_ADDRESS: process.env['TEZOS_STATE_ADDRESS']!,
        TEZOS_BRIDGE_ADDRESS: process.env['TEZOS_BRIDGE_ADDRESS']!,
        TEZOS_LATEST_UNWRAP_NONCE: Number(process.env['TEZOS_LATEST_UNWRAP_NONCE']!),
        TEZOS_PRIVATE_KEY: process.env['TEZOS_PRIVATE_KEY']!,
        ETHEREUM_RPC: process.env['ETHEREUM_RPC']!,
        ETHEREUM_FINALITY: Number(process.env['ETHEREUM_FINALITY']!),
        ETHEREUM_PRIVATE_KEY: process.env['ETHEREUM_PRIVATE_KEY']!,
        EVM_BRIDGE_ADDRESS: process.env['EVM_BRIDGE_ADDRESS']!,
    };
    // Validate environment variables
    Object.entries(env).forEach(([key, value]) => {
        if (value != 0 && !value) {
            Logger.error(`\nEnvironment variable ${key} is required!\n`);
            process.exit(1);
        }
    });
    return env;
}

run_monitor(getEnv());

// Do not let the process crash on async exceptions
process.on('uncaughtException', function (...err) {
    Logger.debug('Caught an exception: ', err);
});
