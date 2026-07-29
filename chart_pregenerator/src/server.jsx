import React from 'react'
import ReactDOMServer from 'react-dom/server'
import express from 'express'
import { Resvg } from '@resvg/resvg-js'
import {
	generateBarChartSVG,
	generateHexbinUSMapSVG,
	generateTreemapChartSVG,
	generateUSMapSVG,
} from './lib'

const PORT = process.env.PORT || 3000
const app = express()

const getRenderScale = (req) => {
	try {
		return JSON.parse(req?.query?.options || '{}').scale || 1
	} catch (e) {
		return 1
	}
}

const renderPng = (svg, scale) => {
	const resvg = new Resvg(svg, {
		font: { defaultFontFamily: 'Arial' },
		// zoom rasterizes at scale × the SVG's size, for hi-res images
		fitTo: { mode: 'zoom', value: scale },
	})
	return resvg.render().asPng()
}

app.get('/', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<p>ok</p>))
})

app.get('/bar-chart.svg', async (req, res) => {
	const component = await generateBarChartSVG(req)

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
})

app.get('/bar-chart.png', async (req, res) => {
	const component = await generateBarChartSVG(req)

	res.setHeader('Content-Type', 'image/png')
	return res.send(renderPng(component, getRenderScale(req)))
})

app.get('/treemap-chart.svg', async (req, res) => {
	const component = await generateTreemapChartSVG(req)

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
})

app.get('/treemap-chart.png', async (req, res) => {
	const component = await generateTreemapChartSVG(req)

	res.setHeader('Content-Type', 'image/png')
	return res.send(renderPng(component, getRenderScale(req)))
})

app.get('/bubble-map.svg', async (req, res) => {
	const component = await generateUSMapSVG(req)

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
})

app.get('/bubble-map.png', async (req, res) => {
	const component = await generateUSMapSVG(req)

	res.setHeader('Content-Type', 'image/png')
	return res.send(renderPng(component, getRenderScale(req)))
})

app.get('/hexbin-map.svg', async (req, res) => {
	const component = await generateHexbinUSMapSVG(req)

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
})

app.get('/hexbin-map.png', async (req, res) => {
	const component = await generateHexbinUSMapSVG(req)

	res.setHeader('Content-Type', 'image/png')
	return res.send(renderPng(component, getRenderScale(req)))
})

app.listen(PORT, () => {
	console.log(`Server is listening on port ${PORT}`)
})
