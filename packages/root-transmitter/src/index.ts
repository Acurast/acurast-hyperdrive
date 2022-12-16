import { run_eth_monitor } from './eth_monitor';
import Logger from './logger';
import { run_tezos_monitor } from './tezos_monitor';

switch (process.argv[2]) {
    case 'ethereum_to_tezos':
        run_eth_monitor();
        break;
    case 'tezos_to_ethereum':
        run_tezos_monitor();
        break;
    default:
        console.log(
            `INVALID OPTION: \"${process.argv[2] || ''}"`,
            '\n\tExpected (ethereum_to_tezos | tezos_to_ethereum)',
        );
}

// Do not let the process crash on async exceptions
process.on('uncaughtException', function (...err) {
    Logger.debug('Caught an exception: ', err);
});
