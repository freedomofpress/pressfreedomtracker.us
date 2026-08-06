// The Dockerfiles copy swc.config.js one level above the working directory, so
// this relative path resolves both in the repo and in the container.
const swcConfig = require('../swc.config')

module.exports = {
	transform: {
		'^.+\\.jsx?$': ['@swc/jest', swcConfig],
	},
	// d3 and friends are ESM-only, so they need transpiling in node_modules.
	transformIgnorePatterns: [
		'<rootDir>/node_modules/(?!d3|tracker|internmap|delaunator|robust-predicates|react-animated-dataset)',
	],
	testPathIgnorePatterns: ['/node_modules/', '<rootDir>/client/'],
}
