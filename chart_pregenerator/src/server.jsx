import React from 'react'
import * as d3 from 'd3'
import fetch from 'node-fetch'
import ReactDOMServer from 'react-dom/server'
import express from 'express'
import { Resvg } from '@resvg/resvg-js'
import BarChart from 'tracker/client/charts/js/components/BarChartMini'
import TreeMap from 'tracker/client/charts/js/components/TreeMapMini'
import USMap from 'tracker/client/charts/js/components/USMap'
import { processIncidentsTimeData } from 'tracker/client/charts/js/components/IncidentsTimeBarChart'
import { filterDatasets } from 'tracker/client/charts/js/lib/utilities'
import { categoriesColors } from 'tracker/client/charts/js/lib/utilities'
import { loadData } from 'tracker/client/charts/js/components/DataLoader'
import { groupByCity, groupByState } from "tracker/client/charts/js/lib/utilities";

const PORT = process.env.PORT || 3000
const app = express()

const FPF_BASE_URL = `http://${process.env.DJANGO_HOST || 'localhost'}:8000`

const chart_height = 800
const chart_width = 1190

const generateBarChartSVG = async (req) => {
	let options = {
		filterTags: null,
		filterCategories: [],
		dateRange: [null, null],
		timePeriod: "months"
	}

	try { options = {...options, ...JSON.parse(req.query.options)} }
	catch (e) {} // do nothing

	const { dataset } = await loadData({
		dataUrl: `${FPF_BASE_URL}/api/edge/incidents/homepage_csv/?`,
		dataKey: 'dataset',
		dataParser: (data) => d3.csvParse(data, d3.autoType),
		fetchFn: fetch
	})

	if (!dataset) return "<svg />";

	try {
		// Filter down to the categories and tags and date range we want
		const filteredDataset = filterDatasets(dataset, options.filterCategories, options.filterTags, options.dateRange)
		const { incidentsByAllTime } = processIncidentsTimeData(filteredDataset, options.timePeriod);

		return ReactDOMServer.renderToString(
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
	} catch (e) {
		return "<svg />";
	}
}

const generateTreemapChartSVG = async (req) => {
	let options = {
		filterTags: null,
		filterCategories: [],
		dateRange: [null, null],
		branch: 'categories'
	}

	try { options = {...options, ...JSON.parse(req.query.options)} }
	catch (e) {} // do nothing

	const dataKey = ['dataset', 'branches']
	const dataUrl = [
		`${FPF_BASE_URL}/api/edge/incidents/?fields=tags%2Cdate%2Ccategories&format=csv`,
		`${FPF_BASE_URL}/api/edge/${options.branch}/`
	]
	const dataParser = [(data) => d3.csvParse(data, d3.autoType), JSON.parse]
	const { dataset, branches } = await loadData({ dataUrl, dataKey, dataParser, fetchFn: fetch })

	if (!dataset) return "<svg />";

	try {
		// Filter down to the categories and tags and date range we want
		const filteredDataset = filterDatasets(dataset, options.filterCategories, options.filterTags, options.dateRange)
		const categoriesColorMap = [...(new Set([...branches.map(d => d.title)]))]
			.reduce(
				(acc, category, i) => ({ ...acc, [category]: categoriesColors[i % categoriesColors.length] }),
				{}
			)

		return ReactDOMServer.renderToString(
			<svg
				xmlns="http://www.w3.org/2000/svg"
				xmlnsXlink="http://www.w3.org/1999/xlink"
				version="1.1"
				width={chart_width}
				height={chart_height}
				viewBox={`0 0 ${chart_width} ${chart_height}`}
			>
				<TreeMap
					data={filteredDataset}
					width={chart_width}
					height={chart_height}
					categoryColumn={'categories'}
					categoriesColors={categoriesColorMap}
					allCategories={Object.keys(categoriesColorMap)}
				/>
			</svg>
		)
	} catch (e) {
		return "<svg />";
	}
}

const generateUSMapSVG = async (req) => {
	let options = {
		filterTags: null,
		filterCategories: [],
		dateRange: [null, null],
		aggregationLocality: 'state'
	}

	try { options = {...options, ...JSON.parse(req.query.options)} }
	catch (e) {} // do nothing

	const { dataset } = await loadData({
		dataUrl: `${FPF_BASE_URL}/api/edge/incidents/homepage_csv/?`,
		dataKey: 'dataset',
		dataParser: (data) => d3.csvParse(data, d3.autoType),
		fetchFn: fetch
	})

	if (!dataset) return "<svg />";

	try {
		const aggregationLocalityMap = {
			state: groupByState,
			city: groupByCity
		}
		const aggregationLocalityFnMap = {
			state: d => d.state,
			city: d => `${d.city}, ${d.state}`
		}

		// Filter down to the categories and tags and date range we want
		const filteredDataset = filterDatasets(dataset, options.filterCategories, options.filterTags, options.dateRange)
		const datasetAggregatedByGeo = filteredDataset && aggregationLocalityMap[options.aggregationLocality](filteredDataset)

		return ReactDOMServer.renderToString(
			<svg
				xmlns="http://www.w3.org/2000/svg"
				xmlnsXlink="http://www.w3.org/1999/xlink"
				version="1.1"
				width={chart_width}
				height={chart_height}
				viewBox={`0 0 ${chart_width} ${chart_height}`}
			>
				<USMap
					data={datasetAggregatedByGeo}
					aggregationLocality={aggregationLocalityFnMap[options.aggregationLocality]}
					width={chart_width}
					height={chart_height}
				/>
			</svg>
		)
	} catch (e) {
		return "<svg />";
	}
}

///////////////////////////////////////////////////////////////////////////////
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
