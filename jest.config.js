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
	transformIgnorePatterns: [
		'<rootDir>/node_modules/(?!d3|internmap|delaunator|robust-predicates|react-animated-dataset)',
	],
	setupFilesAfterEnv: ['<rootDir>/client/common/js/setupTests.js'],
	testPathIgnorePatterns: ['/node_modules/', '<rootDir>/chart_pregenerator/'],
}
