import React from 'react'
import * as d3 from 'd3'
import fetch from 'node-fetch'
import ReactDOMServer from 'react-dom/server'
import express from 'express'
import Resvg from '@resvg/resvg-js'
import BarChart from 'tracker/client/charts/js/components/BarChartMini'
import { processIncidentsTimeData } from 'tracker/client/charts/js/components/IncidentsTimeBarChart'
import { filterDatasets } from 'tracker/client/charts/js/lib/utilities'

const PORT = process.env.PORT || 3000
const app = express()

const chart_height = 800
const chart_width = 1190

app.get('/', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<p>ok</p>))
})

app.get('/bar-chart.svg', async (req, res) => {
	const dataset = d3.csvParse(
		await fetch('http://localhost:8000/api/edge/incidents/homepage_csv/?').then(r => r.text()),
		d3.autoType
	)

	const filterTags = null
	const filterCategories = []
	const dateRange = [null, null]
	const timePeriod = "months"

	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange)

	const { incidentsByAllTime } = processIncidentsTimeData(filteredDataset, timePeriod);

	const component = ReactDOMServer.renderToString(
		<svg
			xmlns="http://www.w3.org/2000/svg"
			xmlnsXlink="http://www.w3.org/1999/xlink"
			version="1.1"
			width={chart_width}
			height={chart_height}
			viewBox={`0 0 ${chart_width} ${chart_height}`}
		>
			<BarChart
				data={incidentsByAllTime}
				x={'date'}
				width={chart_width}
				height={chart_height}
			/>
		</svg>
	)

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
})

app.get('/bar-chart.png', async (req, res) => {
	const dataset = d3.csvParse(
		await fetch('http://localhost:8000/api/edge/incidents/homepage_csv/?').then(r => r.text()),
		d3.autoType
	)

	const filterTags = null
	const filterCategories = []
	const dateRange = [null, null]
	const timePeriod = "months"

	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange)

	const { incidentsByAllTime } = processIncidentsTimeData(filteredDataset, timePeriod);

	const component = ReactDOMServer.renderToString(
		<svg
			xmlns="http://www.w3.org/2000/svg"
			xmlnsXlink="http://www.w3.org/1999/xlink"
			version="1.1"
			width={chart_width}
			height={chart_height}
			viewBox={`0 0 ${chart_width} ${chart_height}`}
		>
			<BarChart
				data={incidentsByAllTime}
				x={'date'}
				width={chart_width}
				height={chart_height}
			/>
		</svg>
	)

	const resvg = new Resvg.Resvg(component)
	const pngData = resvg.render()
	const pngBuffer = pngData.asPng()
	res.setHeader('Content-Type', 'image/png')
	return res.send(pngBuffer)
})

app.get('/bar-chart.svg', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<svg />))
})

app.get('/bar-chart.svg', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<svg />))
})

app.get('/image.png', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<svg />))
})

app.listen(PORT, () => {
	console.log(`Server is listening on port ${PORT}`)
})
