process.traceDeprecation = true;
const path = require("path");
const patternslib_config = require("@patternslib/patternslib/webpack/webpack.config.js");

module.exports = async (env, argv) => {
    let config = {
        entry: {
            collectionfilter: path.resolve(
                __dirname,
                "resources/collectionfilter-config.js"
            ),
        },
    };

    config = patternslib_config(env, argv, config);
    config.output.path = path.resolve(
        __dirname,
        "src/collective/collectionfilter/resources/"
    );
    config.output.filename = "[name].min.js";

    if (process.env.NODE_ENV === "development") {
        config.devServer.static.directory = __dirname;
    }

    return config;
};
