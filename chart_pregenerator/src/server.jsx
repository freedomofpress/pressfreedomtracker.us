import React from 'react'
import * as d3 from 'd3'
import fetch from 'node-fetch'
import ReactDOMServer from 'react-dom/server'
import ReactDOM from 'react-dom'
import Window from 'window'
import express from 'express'
import BarChart from 'tracker/client/charts/js/components/BarChart'
import { processIncidentsTimeData } from 'tracker/client/charts/js/components/IncidentsTimeBarChart'
import { filterDatasets } from 'tracker/client/charts/js/lib/utilities'

const PORT = process.env.PORT || 3000
const app = express()

const chart_height = 800
const chart_width = 1190

const createDOM = () => {
	window = window || new Window();
	const document = window.document;

	const origGlobals = {
		window: global.window,
		document: global.document
	};
	global.window = window;
	global.document = document;

	const container = document.createElement('div');
	container.id = 'root';
	document.body.appendChild(container);

	ReactDOM.render(component, container);

	Object.keys(origGlobals).forEach(prop => {
		global[prop] = origGlobals[prop];
	});

	return container.childNodes[0];
}

app.get('/', (req, res) => {
	return res.send(ReactDOMServer.renderToString(<p>ok</p>))
})

app.get('/bar-chart.svg', async (req, res) => {
	const dataset = d3.csvParse(
		await fetch('http://localhost:8000/api/edge/incidents/homepage_csv/?').then(r => r.text()),
		d3.autoType
	)

	const description = ""
	const filterTags = null
	const filterCategories = []
	const dateRange = [null, null]
	const timePeriod = "months"

	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange)

	const { incidentsByAllTime, xFormat, showByYears } = processIncidentsTimeData(filteredDataset, timePeriod);

	const component = ReactDOMServer.renderToString(
		<BarChart
			description={description}
			data={incidentsByAllTime}
			x={'date'}
			y={'count'}
			xFormat={xFormat}
			tooltipXFormat={d3.utcFormat(showByYears ? "%Y" : "%b %Y")}
			titleLabel={'incidents'}
			width={chart_width}
			height={chart_height}
			isMobileView={false}
		/>
	)

	res.setHeader('Content-Type', 'image/svg+xml')
	return res.send(component)
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
