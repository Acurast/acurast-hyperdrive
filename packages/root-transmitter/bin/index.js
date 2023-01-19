"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const logger_1 = __importDefault(require("./logger"));
const monitor_1 = require("./monitor");
function getEnv() {
    const env = {
        TEZOS_RPC: process.env['TEZOS_RPC'],
        TEZOS_FINALITY: Number(process.env['TEZOS_FINALITY']),
        TEZOS_FINALIZE_SNAPSHOTS: process.env['TEZOS_FINALIZE_SNAPSHOTS'] == '1',
        TEZOS_STATE_ADDRESS: process.env['TEZOS_STATE_ADDRESS'],
        TEZOS_VALIDATOR_ADDRESS: process.env['TEZOS_VALIDATOR_ADDRESS'],
        TEZOS_PRIVATE_KEY: process.env['TEZOS_PRIVATE_KEY'],
        ETHEREUM_RPC: process.env['ETHEREUM_RPC'],
        ETHEREUM_FINALITY: Number(process.env['ETHEREUM_FINALITY']),
        ETHEREUM_PRIVATE_KEY: process.env['ETHEREUM_PRIVATE_KEY'],
        EVM_VALIDATOR_ADDRESS: process.env['EVM_VALIDATOR_ADDRESS'],
    };
    // Validate environment variables
    Object.entries(env).forEach(([key, value]) => {
        if (value != 0 && !value) {
            logger_1.default.error(`\nEnvironment variable ${key} is required!\n`);
            process.exit(1);
        }
    });
    return env;
}
(0, monitor_1.run_monitor)(getEnv());
// Do not let the process crash on async exceptions
process.on('uncaughtException', function (...err) {
    logger_1.default.debug('Caught an exception: ', err);
});
