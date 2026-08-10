module.exports = {
	testEnvironment: 'jsdom',
	verbose: true,
	moduleNameMapper: {
		'^~/(.*)$': '<rootDir>/client/common/js/$1',
		'^WagtailAutocomplete/(.*)$': '<rootDir>/client/autocomplete/js/components/$1',
		'^.+\\.(css|less|scss|sass|svg)$': '<rootDir>/client/common/js/styleMock.js',
	},
	transform: {
		'^.+\\.jsx?$': 'babel-jest',
	},
	// d3 and friends are ESM-only, so they need transpiling in node_modules.
	// The optional `.pnpm/` segment matches pnpm's store layout as well as a
	// flat node_modules.
	transformIgnorePatterns: [
		'node_modules/(?!(\\.pnpm/)?(d3|internmap|delaunator|robust-predicates|react-animated-dataset))',
	],
	setupFilesAfterEnv: ['<rootDir>/client/common/js/setupTests.js'],
	// pnpm's store sits inside the project so it can hard link; it holds temp
	// checkouts of git dependencies, tests and all.
	testPathIgnorePatterns: [
		'/node_modules/',
		'<rootDir>/.pnpm-store/',
		'<rootDir>/chart_pregenerator/',
	],
}
