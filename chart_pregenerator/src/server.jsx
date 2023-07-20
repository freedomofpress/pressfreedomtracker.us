import React from 'react'
import ReactDOMServer from 'react-dom/server'
import express from 'express'
import { Resvg } from '@resvg/resvg-js'
import { generateBarChartSVG, generateTreemapChartSVG, generateUSMapSVG } from './lib'

const PORT = process.env.PORT || 3000
const app = express()

app.get('/', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<p>ok</p>))
})

app.get('/bar-chart.svg', async (req, res) => {
	const component = await generateBarChartSVG(req);

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
})

app.get('/bar-chart.png', async (req, res) => {
	const component = await generateBarChartSVG(req)

	const resvg = new Resvg(component)
	const pngData = resvg.render()
	const pngBuffer = pngData.asPng()
	res.setHeader('Content-Type', 'image/png')
	return res.send(pngBuffer)
})

app.get('/treemap-chart.svg', async (req, res) => {
	const component = await generateTreemapChartSVG(req)

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
})

app.get('/treemap-chart.png', async (req, res) => {
	const component = await generateTreemapChartSVG(req)

	const resvg = new Resvg(component)
	const pngData = resvg.render()
	const pngBuffer = pngData.asPng()
	res.setHeader('Content-Type', 'image/png')
	return res.send(pngBuffer)
})

app.get('/bubble-map.svg', async (req, res) => {
	const component = await generateUSMapSVG(req)

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
})

app.get('/bubble-map.png', async (req, res) => {
	const component = await generateUSMapSVG(req)

	const resvg = new Resvg(component)
	const pngData = resvg.render()
	const pngBuffer = pngData.asPng()
	res.setHeader('Content-Type', 'image/png')
	return res.send(pngBuffer)
})

app.listen(PORT, () => {
	console.log(`Server is listening on port ${PORT}`)
})
