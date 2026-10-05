const { defineConfig } = require("eslint/config");
const fpfEslintConfig = require("fpf-wagtail-common/config/eslint.js");
const globals = require("globals");

const sourceFiles = [
	"client/**/*.{js,jsx}",
	"chart_pregenerator/**/*.{js,jsx}",
	"tracker/**/*.js",
];

module.exports = defineConfig([
	...fpfEslintConfig({
		files: sourceFiles,
		react: true,
		ignores: ["chart_pregenerator/build/", "static/"],
	}),

	{
		files: sourceFiles,
		languageOptions: {
			globals: {
				// webpack's Hot Module Replacement API (module.hot).
				module: "readonly",
				// Matomo's tracking snippet defines this on `window`.
				_paq: "readonly",
			},
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
]);
