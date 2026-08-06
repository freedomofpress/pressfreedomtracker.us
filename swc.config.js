// Shared SWC transform options for webpack (swc-loader) and Jest (@swc/jest),
// including the chart pregenerator's Jest run.
//
// Do not add an `env` block: any `env`, even an empty one, makes SWC resolve the
// browserslist field with its bundled Rust implementation, which cannot parse
// the "baseline widely available" query and panics. eslint-plugin-compat
// consumes browserslist instead.
//
// Omitting `target` falls back to es5. Nothing is polyfilled, so avoid newer
// runtime APIs without a shim.
module.exports = {
	jsc: {
		parser: { syntax: 'ecmascript', jsx: true },
		transform: { react: { runtime: 'classic' } },
		target: 'es2022',
	},
}
