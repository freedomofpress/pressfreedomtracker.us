module.exports = {
	transform: {
		'^.+\\.jsx?$': 'babel-jest',
	},
	// The optional `.pnpm/` segment matches pnpm's store layout as well as a
	// flat node_modules.
	transformIgnorePatterns: [
		'node_modules/(?!(\\.pnpm/)?(d3|tracker|internmap|delaunator|robust-predicates|react-animated-dataset))',
	],
	testPathIgnorePatterns: [
		'/node_modules/',
		'<rootDir>/.pnpm-store/',
		'<rootDir>/client/',
	],
}
