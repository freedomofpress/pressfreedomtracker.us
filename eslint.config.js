const { globalIgnores } = require('eslint/config')

const js = require('@eslint/js')
const react = require('eslint-plugin-react')
const reactHooks = require('eslint-plugin-react-hooks')

module.exports = [
	js.configs.recommended,

	{
		files: ['**/*.js', '**/*.jsx'],

		plugins: {
			react,
			'react-hooks': reactHooks,
		},

		settings: {
			react: {
				version: 'detect',
			},
		},

		languageOptions: {
			ecmaVersion: 2020,
			sourceType: 'module',

			globals: {
				window: true,
				HTMLInputElement: true,
				FormData: true,
				fetch: true,
				document: true,
				module: 'readonly',
			},

			parserOptions: {
				ecmaFeatures: {
					jsx: true,
				},
			},
		},

		rules: {
			'arrow-body-style': 0,
			'prefer-template': 0,
			'no-tabs': 0,
			indent: ['error', 'tab'],
			'no-underscore-dangle': 0,
			'react/jsx-indent': ['error', 'tab'],
			'react/jsx-indent-props': ['error', 'tab'],
			'react/jsx-no-bind': ['warn'],
			'prefer-destructuring': 0,
			radix: ['error', 'as-needed'],
			semi: ['error', 'never'],
			'react/react-in-jsx-scope': 'off',
			'react-hooks/rules-of-hooks': 'error',
			'react-hooks/exhaustive-deps': 'warn',
			'no-unused-vars': 'off',
			'react/jsx-uses-vars': 'error',
		},
	},

	globalIgnores([
		'client/statistics/js/searchstats.js',
		'client/charts/',
		'client/common/js/curlify.js',
		'client/common/js/draftail_curlify.js',
		'**/*.config.js',
		'**/*.test.js',
	]),
]
