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

{
	(async () => {
		const ctx = await esbuild.context(config)
		// Build once before starting nodemon so build/server.js exists — otherwise
		// nodemon crashes on a cold start and its recovery races esbuild.
		await ctx.rebuild()
		await ctx.watch()

		nodemon({
			script: 'build/server.js',
			legacyWatch: true,
			delay: 2000,
			stdin: false,
		})
		nodemon.on('start', () => {
			console.log('App has started')
		}).on('restart', () => {
			console.log('App restarted')
		})
	})()
}
