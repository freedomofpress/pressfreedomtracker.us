// jest.config.js

// Run in UTC so date snapshots don't depend on the machine's timezone.
process.env.TZ = "UTC";

module.exports = {
	testEnvironment: "jsdom",
	verbose: true,
	moduleNameMapper: {
		"^.+\\.(css|less|scss|sass|svg)$":
			"<rootDir>/client/common/js/styleMock.js",
	},
	transformIgnorePatterns: [
		"<rootDir>/node_modules/(?!d3|internmap|delaunator|robust-predicates|react-animated-dataset)",
	],
	setupFiles: ["<rootDir>/client/common/js/setupTests.js"],
	testPathIgnorePatterns: ["/node_modules/", "<rootDir>/chart_pregenerator/"],
};
