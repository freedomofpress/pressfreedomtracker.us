const BundleTracker = require("webpack-bundle-tracker");
const path = require("path");

module.exports = {
	context: __dirname,

	entry: {
		common: "./client/common/js/common.js",
		statistics: "./client/statistics/js/searchstats.js",
		draftail: "./client/common/js/draftail_curlify.js",
		charts: "./client/charts/js/index.js",
		filterSidebar: "./client/charts/js/filter-sidebar.js",
		filterSummary: "./client/charts/js/filter-summary.js",
		searchBar: "./client/common/js/search-bar.js",
		verticalBarChart: "./client/charts/js/vertical-bar-chart.js",
		treeMapChart: "./client/charts/js/tree-map-chart.js",
		bubbleMapChart: "./client/charts/js/bubble-map-chart.js",
		hexbinMapChart: "./client/charts/js/hexbin-map-chart.js",
		"shortcuts-panel": "./client/common/js/shortcuts-panel.js",
	},

	output: {
		path: path.resolve(__dirname, "build/static/bundles"),
		filename: "[name]-[contenthash].js",
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
				include: path.resolve(__dirname, "client"),
			},
			{
				test: /\.scss$/,
				type: "css",
				loader: "sass-loader",
			},
		],
	},

	plugins: [new BundleTracker({ path: __dirname })],
};
