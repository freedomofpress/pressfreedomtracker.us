const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const BundleTracker = require('webpack-bundle-tracker')
const swcConfig = require('./swc.config')

const BASE_DIR = path.join(__dirname, 'client')
const DIST_DIR = path.join(__dirname, 'build/static/bundles')

// `npm run build` passes `--mode production`, `npm run start` passes
// `--mode development`; webpack surfaces that here as `argv.mode`.
module.exports = (env, argv) => {
	const isProd = argv.mode === 'production'

	return {
		// One entry point per output bundle. Each key is the initial file that
		// webpack starts bundling from.
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

		// Production filenames get a content hash for cache-busting; dev keeps the
		// plain entry name. `clean` removes stale bundles left by previous builds.
		output: {
			path: DIST_DIR,
			filename: isProd ? '[name]-[contenthash].js' : '[name].js',
			clean: true,
		},

		// `~` lets JS import from client/common/js without long relative paths;
		// `.jsx` in extensions lets those imports omit the extension.
		resolve: {
			alias: {
				'~': path.resolve(BASE_DIR, 'common/js'),
			},
			extensions: ['.js', '.jsx'],
		},

		// Loaders run bottom-up. JS/JSX are transpiled by swc-loader (options in
		// ./swc.config.js, shared with Jest). Sass is compiled by sass-loader ->
		// css-loader -> MiniCssExtractPlugin, which writes .css files instead of
		// injecting <style> tags.
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
								// The stylesheets use `@import`, which Dart Sass has
								// deprecated in favour of `@use`.
								sassOptions: {
									silenceDeprecations: ['import', 'global-builtin'],
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
					// Fonts and images referenced from CSS via url() become separate files.
					test: /\.(png|svg|jpg|gif|woff|woff2|eot|ttf|otf)$/,
					type: 'asset/resource',
				},
			],
		},

		plugins: [
			new MiniCssExtractPlugin({
				filename: isProd ? '[name]-[contenthash].css' : '[name].css',
				chunkFilename: isProd ? '[id]-[contenthash].css' : '[id].css',
			}),
			// Django reads this manifest via django-webpack-loader; it must sit
			// alongside the bundles it describes.
			new BundleTracker({
				path: DIST_DIR,
				filename: 'webpack-stats.json',
			}),
		],
	}
}
