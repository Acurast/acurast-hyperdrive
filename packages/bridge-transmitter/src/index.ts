import Logger from './logger';
import { run_monitor } from './monitor';

run_monitor();

// Do not let the process crash on async exceptions
process.on('uncaughtException', function (...err) {
    Logger.debug('Caught an exception: ', err);
});
