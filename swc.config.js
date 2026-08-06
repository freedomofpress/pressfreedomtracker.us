// Shared SWC transform options for webpack (swc-loader) and Jest (@swc/jest),
// including the chart pregenerator's Jest run, so everything transpiles the
// same way.
//
// No `env` block: setting one — even an empty one — makes SWC resolve the
// browserslist field with its bundled Rust implementation, which cannot parse
// the "baseline widely available" query and panics. browserslist is consumed by
// eslint-plugin-compat instead.
//
// target es2022 keeps output lean for modern browsers (roughly "Baseline widely
// available"). Nothing is polyfilled, so avoid newer runtime APIs without a
// shim. Omitting target falls back to es5.
module.exports = {
	jsc: {
		parser: { syntax: 'ecmascript', jsx: true },
		transform: { react: { runtime: 'classic' } },
		target: 'es2022',
	},
}
