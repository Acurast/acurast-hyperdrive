"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var LogLevel;
(function (LogLevel) {
    LogLevel[LogLevel["Debug"] = 10] = "Debug";
    LogLevel[LogLevel["Info"] = 20] = "Info";
    LogLevel[LogLevel["Error"] = 30] = "Error";
})(LogLevel || (LogLevel = {}));
const LOG_LEVEL = process.env['LOG_LEVEL'] || 0;
/**
 * Creates a log level
 * @param {LogLevel} level - Log Level (e.g. log, info, debug, error)
 * @return {LogLevelMethod} Function to write the log with the respective log level prefix.
 */
const createLogLevel = (level) => (...d) => {
    if (level >= LOG_LEVEL) {
        switch (level) {
            case LogLevel.Info:
                return console.info(...d);
            case LogLevel.Debug:
                return console.debug(...d);
            case LogLevel.Error:
                return console.error(...d);
        }
    }
};
const Logger = {
    info: createLogLevel(LogLevel.Info),
    debug: createLogLevel(LogLevel.Debug),
    error: createLogLevel(LogLevel.Error),
};
exports.default = Logger;
