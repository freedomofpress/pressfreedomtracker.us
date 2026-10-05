const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require("path");

const target = __dirname + "/build/static/bundles";

const STATIC_URL = process.env.STATIC_URL || "/common/static/";
const scssData = '$static-url: "' + STATIC_URL + '";';
console.log("Using STATIC_URL", STATIC_URL);

// Exported as a function so the config is defined whenever it's loaded.
module.exports = (env, argv) => {
	// The npm scripts pass --config-node-env, which sets NODE_ENV in the Node
	// process. Use an explicit --mode if given, else NODE_ENV, else webpack's
	// own default, and set `mode` below so this config and webpack agree.
	const mode =
		argv.mode ??
		(process.env.NODE_ENV === "development" ? "development" : "production");
	const isProd = mode === "production";

	// In the bundles themselves, webpack replaces process.env.NODE_ENV based on
	// `mode` (optimization.nodeEnv), so no DefinePlugin is needed.
	return {
		mode,

		entry: {
			common: __dirname + "/client/common/js/common.js",
			statistics: __dirname + "/client/statistics/js/searchstats.js",
			draftail: __dirname + "/client/common/js/draftail_curlify.js",
			charts: __dirname + "/client/charts/js/index.js",
			filterSidebar: __dirname + "/client/charts/js/filter-sidebar.js",
			filterSummary: __dirname + "/client/charts/js/filter-summary.js",
			searchBar: __dirname + "/client/common/js/search-bar.js",
			verticalBarChart: __dirname + "/client/charts/js/vertical-bar-chart.js",
			treeMapChart: __dirname + "/client/charts/js/tree-map-chart.js",
			bubbleMapChart: __dirname + "/client/charts/js/bubble-map-chart.js",
			hexbinMapChart: __dirname + "/client/charts/js/hexbin-map-chart.js",
			"shortcuts-panel": __dirname + "/client/common/js/shortcuts-panel.js",
		},

		output: {
			path: target,
			filename: isProd ? "[name]-[contenthash].js" : "[name].js",
			clean: true,
		},

		resolve: {
			extensions: [".js", ".jsx"],
		},

		module: {
			rules: [
				{
					test: /\.jsx?$/,
					loader: "babel-loader",
					// Babel picks its env from NODE_ENV, which --mode alone doesn't set.
					// Pin it to the resolved mode so preset-react never emits jsxDEV
					// calls, which the production React runtime lacks.
					options: { envName: mode },
					include: [path.join(__dirname, "/client")],
				},
				{
					test: /\.s[ca]ss$/,
					use: [
						MiniCssExtractPlugin.loader,
						"css-loader",
						{
							loader: "sass-loader",

							options: {
								sassOptions: {
									loadPaths: [path.resolve(__dirname, "node_modules/")],
								},
								additionalData: scssData,
							},
						},
					],
				},
				{
					test: /\.css$/,
					use: [MiniCssExtractPlugin.loader, "css-loader"],
				},
				{
					test: /\.(png|svg|jpg|gif)$/,
					type: "asset/resource",
				},
				{
					test: /\.(woff|woff2|eot|ttf|otf)$/,
					type: "asset/resource",
				},
			],
		},

		plugins: [
			new MiniCssExtractPlugin({
				filename: isProd ? "[name]-[contenthash].css" : "[name].css",
				chunkFilename: isProd ? "[id]-[contenthash].css" : "[id].css",
			}),
			new BundleTracker({
				path: target,
				filename: "webpack-stats.json",
			}),
		],
	};
};
