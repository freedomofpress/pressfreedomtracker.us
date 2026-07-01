module.exports = {
	"extends": "airbnb",

	"ignorePatterns": [
		"client/statistics/js/searchstats.js",
		"client/charts/",
		"client/common/js/curlify.js",
		"client/common/js/draftail_curlify.js",
		"*.config.js",
		"*.test.js"
	],

	"plugins": [
		"react"
	],

	"settings": {
		"import/resolver": {
			webpack: {
				config: {
					extensions: ['.js', '.jsx']
				}
			}
		}
	},

	"parserOptions": {
		"ecmaFeatures": {
			"experimentalObjectRestSpread": true
		},
		"ecmaVersion": 2020
	},

	"globals": {
		"window": true,
		"HTMLInputElement": true,
		"FormData": true,
		"fetch": true,
		"document": true,
		"import": true,
		"HTMLElement": true,
		"customElements": true,
	},

	"rules": {
		"arrow-body-style": 0,
		"prefer-template": 0,
		"no-tabs": 0,
		"indent": ["error", "tab"],
		"no-underscore-dangle": 0,
		"react/jsx-indent": ["error", "tab"],
		"react/jsx-indent-props": ["error", "tab"],
		"react/jsx-no-bind": ["warn"],
		"prefer-destructuring": 0,
		"import/no-unresolved": 0,
		"radix": ["error", "as-needed"],
		"semi": ["error", "never"]
	},

	"overrides": [
		{
			// The chart pregenerator is a Node service (not browser code), so
			// console logging is expected. It also imports shared chart
			// components without file extensions (resolved by esbuild/babel/jest).
			"files": ["chart_pregenerator/**/*.js", "chart_pregenerator/**/*.jsx"],
			"env": { "node": true },
			"rules": {
				"no-console": "off",
				"import/extensions": "off"
			}
		}
	]
};
