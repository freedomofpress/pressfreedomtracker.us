const esbuild = require("esbuild")

{
	(async () => {
		await esbuild.build({
			entryPoints: ['src/server.jsx'],
			bundle: true,
			outfile: 'build/server.js',
			platform: 'node',
			loader: { '.node': 'copy' },
			plugins: [],
		})
	})()
}
