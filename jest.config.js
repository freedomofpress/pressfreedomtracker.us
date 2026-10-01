// jest.config.js
module.exports = {
	testEnvironment: "jsdom",
	verbose: true,
	moduleNameMapper: {
		"^WagtailAutocomplete/(.*)$":
			"<rootDir>/client/autocomplete/js/components/$1",
		"^.+\\.(css|less|scss|sass|svg)$": "babel-jest",
	},
	transformIgnorePatterns: [
		"<rootDir>/node_modules/(?!d3|internmap|delaunator|robust-predicates|react-animated-dataset)",
	],
	setupFiles: ["<rootDir>/client/common/js/setupTests.js"],
	testPathIgnorePatterns: ["/node_modules/", "<rootDir>/chart_pregenerator/"],
};
