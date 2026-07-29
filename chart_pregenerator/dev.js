/* eslint-disable import/no-extraneous-dependencies */
const path = require('path')
const esbuild = require('esbuild')
const nodemon = require('nodemon')

const config = {
	entryPoints: ['src/server.jsx'],
	bundle: true,
	platform: 'node',
	outfile: path.join(process.cwd(), 'build/server.js'),
	loader: { '.node': 'copy' },
	plugins: [],
	logLevel: 'info',
}

// eslint-disable-next-line no-lone-blocks
{
	(async () => {
		let ctx = await esbuild.context(config)
		// Build once before starting nodemon so build/server.js exists — otherwise
		// nodemon crashes on a cold start and its recovery races esbuild (flaky CI).
		await ctx.rebuild()
		await ctx.watch()

		nodemon({
			script: 'build/server.js',
			legacyWatch: true,
			delay: 2000,
			stdin: false,
		})
		nodemon.on("start", () => {
			console.log("App has started")
		}).on("restart", () => {
			console.log("App restarted")
		})
	})()
}
