type LogLevel = 'trace' | 'log' | 'info' | 'debug' | 'error' | 'warn';
type LogLevelMethod = (...d: unknown[]) => void;

/**
 * Creates a log level
 * @param {LogLevel} level - Log Level (e.g. log, info, debug, error)
 * @return {LogLevelMethod} Function to write the log with the respective log level prefix.
 */
const createLogLevel =
    (level: LogLevel): LogLevelMethod =>
    (...d) => {
        if (process.env.NODE_ENV === 'development') {
            console.trace(`[${level.toUpperCase()}]`, ...d);
        }
    };

const Logger = {
    log: createLogLevel('log'),
    info: createLogLevel('info'),
    debug: createLogLevel('debug'),
    error: createLogLevel('error'),
    trace: createLogLevel('trace'),
    warn: createLogLevel('warn'),
};

export default Logger;
