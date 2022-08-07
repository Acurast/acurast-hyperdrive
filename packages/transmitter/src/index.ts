import { run_eth_monitor } from './eth_monitor';
import { run_tezos_monitor } from './tezos_monitor';

switch (process.argv[2]) {
    case 'eth_monitor':
        run_eth_monitor();
        break;
    case 'tezos_monitor':
        run_tezos_monitor();
        break;
    default:
        console.log('INVALID OPTION', process.argv[2]);
}
