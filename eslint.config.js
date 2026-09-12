const js = require('@eslint/js')
const react = require('eslint-plugin-react')
const reactHooks = require('eslint-plugin-react-hooks')
const jsxA11y = require('eslint-plugin-jsx-a11y')
const importPlugin = require('eslint-plugin-import')
const prettier = require('eslint-config-prettier')
const globals = require('globals')

const jsFiles = [
	'client/**/*.js',
	'client/**/*.jsx',
	'chart_pregenerator/**/*.js',
	'chart_pregenerator/**/*.jsx',
]

module.exports = [
	{
		ignores: [
			'client/statistics/js/searchstats.js',
			'client/charts/**',
			'client/common/js/curlify.js',
			'client/common/js/draftail_curlify.js',
			'**/*.test.js',
			'coverage/**',
			'build/**',
		],
	},

	{ files: jsFiles, ...js.configs.recommended },
	{ files: jsFiles, ...react.configs.flat.recommended },
	{ files: jsFiles, ...jsxA11y.flatConfigs.recommended },
	{ files: jsFiles, ...importPlugin.flatConfigs.recommended },
	{ files: jsFiles, ...prettier },

	{
		files: jsFiles,

		languageOptions: {
			// eslint-plugin-import's recommended config hardcodes ecmaVersion: 2018,
			// which is older than this codebase's syntax (e.g. optional chaining).
			// Override it back to the ESLint default so parsing doesn't regress.
			ecmaVersion: 'latest',
			globals: {
				...globals.browser,
				// webpack injects a `module` binding into each bundled chunk for
				// its Hot Module Replacement API (module.hot).
				module: 'readonly',
			},
		},

		settings: {
			react: {
				version: 'detect',
			},
			'import/resolver': {
				webpack: {
					config: {
						extensions: ['.js', '.jsx'],
					},
				},
			},
		},

		plugins: {
			'react-hooks': reactHooks,
		},

		rules: {
			'react-hooks/rules-of-hooks': 'error',
			'react-hooks/exhaustive-deps': 'warn',

			// webpack.config.js only populates module.exports when run via the
			// `build`/`start` npm scripts (it branches on npm_lifecycle_event),
			// so requiring it here (e.g. from eslint-import-resolver-webpack)
			// yields an empty config and can't actually resolve aliases or
			// extension-less imports. Leave path resolution unchecked until
			// that export is restructured.
			'import/no-unresolved': 'off',
		},
	},

	{
		// The chart pregenerator is a Node service (not browser code), so
		// console logging is expected. It also imports shared chart
		// components without file extensions (resolved by esbuild/babel/jest).
		files: ['chart_pregenerator/**/*.js', 'chart_pregenerator/**/*.jsx'],
		languageOptions: {
			globals: {
				...globals.node,
			},
		},
		rules: {
			'no-console': 'off',
			'import/extensions': 'off',
		},
	},
]
