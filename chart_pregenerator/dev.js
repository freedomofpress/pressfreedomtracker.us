const path = require('path')
const esbuild = require("esbuild")
const relativeDeps = require("relative-deps")
const chokidar = require("chokidar")
const nodemon = require('nodemon');

const config = {
	entryPoints: ["src/server.jsx"],
	bundle: true,
	platform: "node",
	outfile: path.join(process.cwd(), "build/server.js"),
	loader: { ".node": "copy" },
	plugins: [],
}

{
	(async () => {
		await relativeDeps.installRelativeDeps()
		await esbuild.build(config)

		chokidar.watch(
			["../client/**/*.js", "../client/**/*.jsx", "./src/**/*.js", "./src/**/*.jsx"],
			{ ignoreInitial: true, }
		)
			.on('all', async (event, path) => {
					console.log('\nChanges detected, rebuilding app...');
					await relativeDeps.installRelativeDeps()
					await esbuild.build(config)
			})

		nodemon({
			script: 'build/server.js',
			delay: 2000,
		});

		nodemon.on('start', function () {
			console.log('App has started');
		}).on('quit', function () {
			console.log('App has quit');
			process.exit();
		}).on('restart', async function () {
			console.log('App restarted');
		});
	})();
}
