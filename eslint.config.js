const js = require('@eslint/js')
const globals = require('globals')
const react = require('eslint-plugin-react')
const reactHooks = require('eslint-plugin-react-hooks')
const jsxA11y = require('eslint-plugin-jsx-a11y')
const compat = require('eslint-plugin-compat')

module.exports = [
	// Only hand-written source is linted; everything below is build output,
	// generated, or vendored.
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

			// Carried over from the previous .eslintrc.js, which excluded these.
			'client/common/js/curlify.js',
			'client/common/js/curlify.test.js',

			// FIXME: client/charts/ has never been linted — the previous
			// .eslintrc.js excluded it too. It currently reports 58 errors,
			// including 5 conditional hook calls in App.jsx and BarChart.jsx.
			// Fixing those is a follow-up; this carve-out is temporary and
			// deliberately explicit so it isn't forgotten again.
			'client/charts/**',
		],
	},

	js.configs.recommended,

	// Browser-shipped app source. eslint-plugin-compat flags any JS API that
	// isn't Baseline-widely-available for the browsers in package.json's
	// "browserslist" field.
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

	// React source and the JSX-using Jest specs (some are .js). Classic runtime
	// -> React must be in scope, which react/recommended enforces.
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

	// The chart pregenerator is a Node service, so logging is expected.
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

	// Jest specs.
	{
		files: [
			'**/*.test.{js,jsx}',
			'**/__tests__/**/*.{js,jsx}',
			'client/charts/js/tests/**/*.{js,jsx}',
		],
		languageOptions: { globals: { ...globals.jest } },
	},

	// Build/tooling config files run in Node as CommonJS.
	{
		files: ['*.config.js', 'chart_pregenerator/*.js'],
		languageOptions: {
			sourceType: 'commonjs',
			globals: { ...globals.node },
		},
	},
]
