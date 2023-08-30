module.exports = {
	transform: {
		"^.+\\.jsx?$": "babel-jest"
	},
	transformIgnorePatterns: [
		'<rootDir>/node_modules/(?!d3|tracker|internmap|delaunator|robust-predicates|react-animated-dataset)',
	],
	testPathIgnorePatterns: ['/node_modules/', '<rootDir>/client/'],
}
