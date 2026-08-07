module.exports = (api) => ({
	presets: [
		// The default `modules: 'auto'` keeps ESM for webpack and emits CommonJS
		// for Jest.
		['@babel/preset-env', api.env('test') ? { targets: { node: 'current' } } : {}],
		// Falls back to the slower dev JSX runtime unless NODE_ENV is production,
		// which the npm scripts set.
		'@babel/preset-react',
	],
})
