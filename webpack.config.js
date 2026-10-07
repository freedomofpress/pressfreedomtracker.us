const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require("path");

const isProd = process.env.npm_lifecycle_event === "build";
const isDev = process.env.npm_lifecycle_event === "start";

const target = __dirname + "/build/static/bundles";

const STATIC_URL = process.env.STATIC_URL || "/common/static/";
const scssData = '$static-url: "' + STATIC_URL + '";';
console.log("Using STATIC_URL", STATIC_URL);

const common = {
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
		filename: "[name].js",
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
				// webpack's --mode doesn't set NODE_ENV for the Node process, so
				// without this Babel defaults to 'development' and preset-react
				// emits jsxDEV calls, which the production React runtime lacks.
				options: { envName: isProd ? "production" : "development" },
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
			filename: "[name]-[hash].css",
			chunkFilename: "[id]-[hash].css",
		}),
		new BundleTracker({
			path: target,
			filename: "webpack-stats.json",
		}),
	],
};

if (isProd) {
	module.exports = {
		...common,
		output: {
			...common.output,
			filename: "[name]-[contenthash].js",
		},
		plugins: [
			...common.plugins,
			new webpack.DefinePlugin({
				"process.env": { NODE_ENV: JSON.stringify("production") },
			}),
		],
	};
}

if (isDev) {
	module.exports = {
		...common,
		output: {
			...common.output,
			filename: "[name]-[contenthash].js",
			pathinfo: true,
		},
	};
}
