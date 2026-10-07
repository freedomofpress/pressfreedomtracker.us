const { defineConfig, globalIgnores } = require("eslint/config");
const js = require("@eslint/js");
const react = require("eslint-plugin-react");
const reactHooks = require("eslint-plugin-react-hooks");
const jsxA11y = require("eslint-plugin-jsx-a11y");
const importPlugin = require("eslint-plugin-import");
const globals = require("globals");

module.exports = defineConfig([
	globalIgnores([
		"build/",
		"**/coverage/",
		"htmlcov/",
		"chart_pregenerator/build/",
		"static/",
		".venv/",
	]),

	{
		files: [
			"client/**/*.{js,jsx}",
			"chart_pregenerator/**/*.{js,jsx}",
			"tracker/**/*.js",
		],
		extends: [
			js.configs.recommended,
			react.configs.flat.recommended,
			jsxA11y.flatConfigs.recommended,
			importPlugin.flatConfigs.recommended,
			importPlugin.flatConfigs.react,
		],
		plugins: {
			"react-hooks": reactHooks,
		},
		languageOptions: {
			// eslint-plugin-import's recommended config sets ecmaVersion: 2018,
			// which can't parse newer syntax such as optional chaining.
			ecmaVersion: "latest",
			globals: {
				...globals.browser,
				// webpack's Hot Module Replacement API (module.hot).
				module: "readonly",
				// Matomo's tracking snippet defines this on `window`.
				_paq: "readonly",
			},
		},
		settings: {
			react: {
				version: "detect",
			},
			"import/resolver": { node: { extensions: [".js", ".jsx"] } },
		},
		rules: {
			"react-hooks/rules-of-hooks": "error",
			"react-hooks/exhaustive-deps": "warn",

			// prop-types is going away in React 19
			"react/prop-types": "off",
		},
	},

	{
		files: ["**/*.test.js"],
		languageOptions: {
			globals: globals.jest,
		},
	},

	{
		// The chart pregenerator is a Node service.
		files: ["chart_pregenerator/**/*.{js,jsx}"],
		languageOptions: {
			globals: globals.node,
		},
		rules: {
			// pregenerator's ../client imports and its own packages only resolve in its container.
			"import/no-unresolved": "off",
		},
	},

	{
		// Build tool configs at the repo root, which run in Node.
		files: ["*.config.{js,mjs}"],
		extends: [js.configs.recommended],
		languageOptions: {
			globals: globals.node,
		},
	},

	{
		files: ["*.config.js"],
		languageOptions: {
			sourceType: "commonjs",
		},
	},
]);
