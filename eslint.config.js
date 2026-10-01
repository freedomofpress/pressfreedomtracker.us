const { defineConfig, globalIgnores } = require("eslint/config");
const js = require("@eslint/js");
const react = require("eslint-plugin-react");
const reactHooks = require("eslint-plugin-react-hooks");
const jsxA11y = require("eslint-plugin-jsx-a11y");
const importPlugin = require("eslint-plugin-import");
const globals = require("globals");

const jsFiles = [
	"client/**/*.js",
	"client/**/*.jsx",
	"chart_pregenerator/**/*.js",
	"chart_pregenerator/**/*.jsx",
	"tracker/**/*.js",
];

// Top-level build tooling config files (babel.config.js, webpack.config.js,
// etc.), not matched by "*.config.js" for files nested in subdirectories.
const nodeConfigFiles = ["*.config.js"];

module.exports = defineConfig([
	globalIgnores([
		"build/static/js/picturefill.3.0.2.min.js",
		"coverage/**",
		"build/**",
		"chart_pregenerator/build/**",
		"static/**",
		".venv/**",
	]),

	{
		files: jsFiles,
		extends: [
			js.configs.recommended,
			react.configs.flat.recommended,
			jsxA11y.flatConfigs.recommended,
			importPlugin.flatConfigs.recommended,
		],

		languageOptions: {
			// eslint-plugin-import's recommended config hardcodes ecmaVersion: 2018,
			// which is older than this codebase's syntax (e.g. optional chaining).
			// Override it back to the ESLint default so parsing doesn't regress.
			ecmaVersion: "latest",
			globals: {
				...globals.browser,
				// webpack injects a `module` binding into each bundled chunk for
				// its Hot Module Replacement API (module.hot).
				module: "readonly",
				// Matomo/Piwik's tracking snippet defines this on `window` before
				// our bundles run.
				_paq: "readonly",
			},
		},

		settings: {
			react: {
				version: "detect",
			},
		},

		plugins: {
			"react-hooks": reactHooks,
		},

		rules: {
			"react-hooks/rules-of-hooks": "error",
			"react-hooks/exhaustive-deps": "warn",

			// webpack.config.js only populates module.exports when run via the
			// `build`/`start` npm scripts (it branches on npm_lifecycle_event),
			// so requiring it here (e.g. from eslint-import-resolver-webpack)
			// yields an empty config and can't actually resolve aliases or
			// extension-less imports. Leave path resolution unchecked until
			// that export is restructured.
			"import/no-unresolved": "off",

			// prop-types is going away in React 19
			"react/prop-types": "off",
		},
	},

	{
		files: ["**/*.test.js"],
		languageOptions: {
			globals: {
				...globals.jest,
			},
		},
	},

	{
		// The chart pregenerator is a Node service (not browser code), so
		// console logging is expected. It also imports shared chart
		// components without file extensions (resolved by esbuild/babel/jest).
		files: ["chart_pregenerator/**/*.js", "chart_pregenerator/**/*.jsx"],
		languageOptions: {
			globals: {
				...globals.node,
			},
		},
		rules: {
			"no-console": "off",
			"import/extensions": "off",
		},
	},

	{
		files: nodeConfigFiles,
		extends: [js.configs.recommended],
		languageOptions: {
			ecmaVersion: "latest",
			sourceType: "commonjs",
			globals: {
				...globals.node,
			},
		},
	},
]);
