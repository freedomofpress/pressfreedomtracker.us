module.exports = {
	presets: ["@babel/preset-env", "@babel/preset-react"],
	overrides: [
		{
			// client/statistics requires classic runtime for compatibility since
			// it is a Draftail plugin intended to be rendered by Wagtail's React.
			test: "./client/statistics",
			presets: [["@babel/preset-react", { runtime: "classic" }]],
		},
	],
};
