const js = require('@eslint/js')
const globals = require('globals')
const react = require('eslint-plugin-react')
const reactHooks = require('eslint-plugin-react-hooks')
const jsxA11y = require('eslint-plugin-jsx-a11y')
const compat = require('eslint-plugin-compat')

module.exports = [
	{
		ignores: [
			'build/**',
			'dist/**',
			'coverage/**',
			'htmlcov/**',
			'media/**',
			'node_modules/**',
			'chart_pregenerator/build/**',
			'chart_pregenerator/node_modules/**',
			'tracker/static/**', // vendored, e.g. piwik.js
			'**/*.min.js',
			'webpack-stats.json',

			'client/common/js/curlify.js',
			'client/common/js/curlify.test.js',

			// FIXME: not yet linted — reports 58 errors, including 5 conditional
			// hook calls in App.jsx and BarChart.jsx.
			'client/charts/**',
		],
	},

	js.configs.recommended,

	// eslint-plugin-compat flags JS APIs outside the "browserslist" range in
	// package.json.
	{
		...compat.configs['flat/recommended'],
		files: ['client/**/*.{js,jsx}'],
		languageOptions: {
			ecmaVersion: 2023,
			sourceType: 'module',
			globals: {
				...globals.browser,
				// webpack's hot-module-reload API.
				module: 'readonly',
			},
			parserOptions: { ecmaFeatures: { jsx: true } },
		},
	},

	// Classic JSX runtime, so React must be in scope — react/recommended
	// enforces that.
	{
		files: ['client/**/*.{js,jsx}', 'chart_pregenerator/src/**/*.{js,jsx}'],
		plugins: {
			react,
			'react-hooks': reactHooks,
			'jsx-a11y': jsxA11y,
		},
		settings: { react: { version: 'detect' } },
		rules: {
			...react.configs.flat.recommended.rules,
			...jsxA11y.flatConfigs.recommended.rules,
			'react-hooks/rules-of-hooks': 'error',
			'react-hooks/exhaustive-deps': 'warn',
			// React 19 ignores propTypes at runtime; don't require them.
			'react/prop-types': 'off',
			// Allow intentionally-unused catch bindings and `_`-prefixed names.
			'no-unused-vars': [
				'error',
				{
					argsIgnorePattern: '^_',
					varsIgnorePattern: '^_',
					caughtErrors: 'none',
				},
			],
		},
	},

	// The pregenerator is a Node service, so logging is expected.
	{
		files: ['chart_pregenerator/**/*.{js,jsx}'],
		languageOptions: {
			ecmaVersion: 2023,
			sourceType: 'module',
			globals: { ...globals.node },
			parserOptions: { ecmaFeatures: { jsx: true } },
		},
		rules: { 'no-console': 'off' },
	},

	{
		files: [
			'**/*.test.{js,jsx}',
			'**/__tests__/**/*.{js,jsx}',
			'client/charts/js/tests/**/*.{js,jsx}',
		],
		languageOptions: { globals: { ...globals.jest } },
	},

	{
		files: ['*.config.js', 'chart_pregenerator/*.js'],
		languageOptions: {
			sourceType: 'commonjs',
			globals: { ...globals.node },
		},
	},
]
