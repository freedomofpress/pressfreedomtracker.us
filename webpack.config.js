const fpfWebpackConfig = require("fpf-wagtail-common/config/webpack.js");

module.exports = {
	...fpfWebpackConfig({
		rootDir: __dirname,
		entry: {
			common: "./client/common/js/common.js",
			statistics: {
				import: "./client/statistics/js/searchstats.js",
				layer: "wagtail-admin",
			},
			draftail: "./client/common/js/draftail_curlify.js",
			charts: "./client/charts/js/index.js",
			filterSidebar: "./client/charts/js/filter-sidebar.js",
			filterSummary: "./client/charts/js/filter-summary.js",
			searchBar: "./client/common/js/search-bar.js",
			verticalBarChart: "./client/charts/js/vertical-bar-chart.js",
			treeMapChart: "./client/charts/js/tree-map-chart.js",
			bubbleMapChart: "./client/charts/js/bubble-map-chart.js",
			hexbinMapChart: "./client/charts/js/hexbin-map-chart.js",
			"shortcuts-panel": "./client/common/js/shortcuts-panel.js",
		},
	}),

	// The statistics entry (wagtail-admin layer) is for a Draftail plugin intended to
	// be rendered by Wagtail's React. React imports anywhere in that bundle should resolve
	// to globals that Wagtail will provide at runtime, instead of our bundled copy.
	externals: {
		byLayer: {
			"wagtail-admin": { react: "React", "react-dom": "ReactDOM" },
		},
	},
};
