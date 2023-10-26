/* eslint-disable import/no-extraneous-dependencies */
const path = require('path')
const esbuild = require('esbuild')
const chokidar = require('chokidar')
const fs = require('fs-extra')
const debounce = require('lodash.debounce')
const nodemon = require('nodemon')

const config = {
	entryPoints: ['src/server.jsx'],
	bundle: true,
	platform: 'node',
	outfile: path.join(process.cwd(), 'build/server.js'),
	loader: { '.node': 'copy' },
	plugins: [],
}

// eslint-disable-next-line no-lone-blocks
{
	(async () => {
		fs.copySync('../client', './client')
		await esbuild.build(config)

		const rebuild = debounce(async () => {
			console.log('\nChanges detected, rebuilding app...')
			fs.copySync('../client', './client')
			await esbuild.build(config)
		}, 2000)

		chokidar.watch(
			['../client/**/*.js', '../client/**/*.jsx', './src/**/*.js', './src/**/*.jsx'],
			{ ignoreInitial: true },
		)
			.on('all', () => {
				rebuild.cancel()
				rebuild()
			})

		const runApp = () => {
			nodemon({
				script: 'build/server.js',
				delay: 2000,
			})

			nodemon.on('start', () => {
				console.log('App has started')
			}).on('restart', async () => {
				console.log('App restarted')
			}).on('crash', async () => {
				console.log('App crashed, restarting...')
				nodemon.emit('quit')
				runApp()
			})
		}

		runApp()
	})()
}
