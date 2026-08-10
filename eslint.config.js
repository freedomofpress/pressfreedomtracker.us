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
			'coverage/**',
			'htmlcov/**',
			'media/**',
			'node_modules/**',
			'.pnpm-store/**',
			'chart_pregenerator/build/**',
			'chart_pregenerator/node_modules/**',
			'tracker/static/**',
			'**/*.min.js',
			'webpack-stats.json',

			'client/common/js/curlify.js',
			'client/common/js/draftail_curlify.js',
			'client/statistics/js/searchstats.js',

			// FIXME: never linted. Enabling these reports ~440 problems.
			'client/charts/**',
			'**/*.test.js',
			'**/__tests__/**',
		],
	},

	js.configs.recommended,

	// Flags JS APIs outside the "browserslist" range in package.json.
	{
		...compat.configs['flat/recommended'],
		files: ['client/**/*.{js,jsx}'],
		languageOptions: {
			ecmaVersion: 2023,
			sourceType: 'module',
			globals: {
				...globals.browser,
				module: 'readonly',
			},
			parserOptions: { ecmaFeatures: { jsx: true } },
		},
	},

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
			'react/prop-types': 'off',
			'no-console': 'warn',
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
		files: ['*.config.js', 'chart_pregenerator/*.js'],
		languageOptions: {
			sourceType: 'commonjs',
			globals: { ...globals.node },
		},
	},
]
