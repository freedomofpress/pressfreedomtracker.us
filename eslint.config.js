const fpfEslintConfig = require("fpf-wagtail-common/config/eslint.js");
const globals = require("globals");

const jsFiles = [
	"client/**/*.js",
	"client/**/*.jsx",
	"chart_pregenerator/**/*.js",
	"chart_pregenerator/**/*.jsx",
];

module.exports = [
	{
		ignores: ["coverage/**", "build/**"],
	},

	...fpfEslintConfig(jsFiles),

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
];
