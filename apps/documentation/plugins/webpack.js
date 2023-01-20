
module.exports = function (context, options) {
    return {
        name: "webpack-polyfills",
        configureWebpack(config, isServer) {
            return {
                resolve: {
                    fallback: {
                        stream: require.resolve('stream-browserify'),
                    }
                }
            };
        },
    };
};
