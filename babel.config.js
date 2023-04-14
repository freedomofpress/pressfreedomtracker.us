// babel.config.js
module.exports = (api) => {
	const isTest = api.env('test')
	if (isTest) {
		return {
			presets: [
				[
					'@babel/preset-env',
					{
						modules: false,
						targets: {
							node: 'current',
						},
					},
				],
				'@babel/preset-react',
			],
			plugins: [
				'@babel/plugin-transform-modules-commonjs',
			],
		}
	}
	return {
		presets: [
			[
				'@babel/preset-env',
				{
					modules: false,
				},
			],
			'@babel/preset-react',
		],
	}
}
