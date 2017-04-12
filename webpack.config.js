var webpack       = require('webpack');
var merge         = require('webpack-merge');
var autoprefixer  = require('autoprefixer');
var BundleTracker = require('webpack-bundle-tracker');
var path = require('path');

var TARGET = process.env.npm_lifecycle_event;
process.env.BABEL_ENV = TARGET;

var target = __dirname + '/common/static/js/bundles';

var postCSSPlugins = function() {
	return {
		defaults: [autoprefixer],
		cleaner: [autoprefixer({ browsers: [
			'Chrome >= 35',
			'Firefox >= 31',
			'Edge >= 12',
			'Explorer >= 9',
			'iOS >= 8',
			'Safari >= 8',
			'Android 2.3',
			'Android >= 4',
			'Opera >= 12'
		]})]
	}
}

var common = {
	entry: {
		common: __dirname + '/common/static/js/common.js',
	},

	output: {
		path: target,
		filename: '[name].js'
	},

	resolve: {
		alias: {
			'~': __dirname + '/core/static/js',
			modernizr$: path.resolve(__dirname, '.modernizrrc')
		},
		extensions: ['.js', '.jsx'],
		modules: ['node_modules']
	},

	module: {
		rules: [
			{
				test: /\.jsx?$/,
				use: [
					{
						loader: 'babel-loader',
						query: {
							presets: ['react', 'es2015', 'stage-0', 'stage-1', 'stage-2'],
							plugins: ['add-module-exports']
						},
					}
				],
				include: [
					path.join(__dirname, '/core/static/js'),
				],
			},
			{
				test: /\.s[ca]ss$/,
				use: [
					'style-loader',
					'css-loader',
					{
						loader: 'postcss-loader',
						options: {
							plugins: postCSSPlugins
						}
					},
					{
						loader: 'sass-loader',
						options: {
							includePaths: [path.resolve(__dirname, 'node_modules/')]
						}
					}
				],
			},
			{
				test: /\.css$/,
				use: [
					'style-loader',
					'css-loader',
					{
						loader: 'postcss-loader',
						options: {
							plugins: postCSSPlugins
						}
					}
				]
			},
			// Currently unused, but we'll want it if we install modernizr:
			{
				test: /\.modernizrrc$/,
				use: ['modernizr']
			}
		]
	},

	plugins: [
		new BundleTracker({
			path: target,
			filename: './webpack-stats.json'
		})
	]
};

if (TARGET === 'build') {
	module.exports = merge(common, {
		output: {
			filename: '[name]-[hash].js'
		},
		plugins: [
			new webpack.DefinePlugin({
				'process.env': { 'NODE_ENV': JSON.stringify('production') }
			})
		]
	});
}

if (TARGET === 'start') {
	module.exports = merge(common, {
		devtool: 'eval-source-map',
		devServer: {
			contentBase: target,
			progress: true,
		}
	});
}
