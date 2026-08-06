const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const BundleTracker = require('webpack-bundle-tracker')
const swcConfig = require('./swc.config')

const BASE_DIR = path.join(__dirname, 'client')
const DIST_DIR = path.join(__dirname, 'build/static/bundles')

module.exports = {
	entry: {
		common: path.resolve(BASE_DIR, 'common/js/common.js'),
		statistics: path.resolve(BASE_DIR, 'statistics/js/searchstats.js'),
		draftail: path.resolve(BASE_DIR, 'common/js/draftail_curlify.js'),
		charts: path.resolve(BASE_DIR, 'charts/js/index.js'),
		filterSidebar: path.resolve(BASE_DIR, 'charts/js/filter-sidebar.js'),
		filterSummary: path.resolve(BASE_DIR, 'charts/js/filter-summary.js'),
		searchBar: path.resolve(BASE_DIR, 'common/js/search-bar.js'),
		verticalBarChart: path.resolve(BASE_DIR, 'charts/js/vertical-bar-chart.js'),
		treeMapChart: path.resolve(BASE_DIR, 'charts/js/tree-map-chart.js'),
		bubbleMapChart: path.resolve(BASE_DIR, 'charts/js/bubble-map-chart.js'),
		hexbinMapChart: path.resolve(BASE_DIR, 'charts/js/hexbin-map-chart.js'),
	},

	// Django serves these with no Cache-Control, so a stable filename would be
	// served stale from the browser cache.
	output: {
		path: DIST_DIR,
		filename: '[name]-[contenthash].js',
		clean: true,
	},

	resolve: {
		alias: {
			'~': path.resolve(BASE_DIR, 'common/js'),
		},
		extensions: ['.js', '.jsx'],
	},

	module: {
		rules: [
			{
				test: /\.jsx?$/,
				include: [BASE_DIR],
				use: { loader: 'swc-loader', options: swcConfig },
			},
			{
				test: /\.s[ca]ss$/,
				use: [
					MiniCssExtractPlugin.loader,
					'css-loader',
					{
						loader: 'sass-loader',
						options: {
							sassOptions: {
								// The stylesheets use `@import`, which Dart Sass has
								// deprecated in favour of `@use`.
								silenceDeprecations: ['import'],
							},
						},
					},
				],
			},
			{
				test: /\.css$/,
				use: [MiniCssExtractPlugin.loader, 'css-loader'],
			},
			{
				test: /\.(png|svg|jpg|gif|woff|woff2|eot|ttf|otf)$/,
				type: 'asset/resource',
			},
		],
	},

	plugins: [
		new MiniCssExtractPlugin({
			filename: '[name]-[contenthash].css',
			chunkFilename: '[id]-[contenthash].css',
		}),
		// django-webpack-loader reads this manifest; it must sit alongside the
		// bundles it describes.
		new BundleTracker({
			path: DIST_DIR,
			filename: 'webpack-stats.json',
		}),
	],
}
