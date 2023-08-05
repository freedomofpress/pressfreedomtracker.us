import * as d3 from 'd3'
import React from 'react'
import ReactDOMServer from 'react-dom/server'
import fetch from 'node-fetch'
import BarChart from 'tracker/client/charts/js/components/BarChart'
import BarChartMini from 'tracker/client/charts/js/components/BarChartMini'
import TreeMap from 'tracker/client/charts/js/components/TreeMap'
import TreeMapMini from 'tracker/client/charts/js/components/TreeMapMini'
import USMap from 'tracker/client/charts/js/components/USMap'
import { processIncidentsTimeData } from 'tracker/client/charts/js/components/IncidentsTimeBarChart'
import { filterDatasets } from 'tracker/client/charts/js/lib/utilities'
import { categoriesColors } from 'tracker/client/charts/js/lib/utilities'
import { loadData } from 'tracker/client/charts/js/components/DataLoader'
import { groupByCity, groupByState } from "tracker/client/charts/js/lib/utilities"

const FPF_BASE_URL = `http://${process.env.DJANGO_HOST || 'localhost'}:8000`

const chart_height = 800
const chart_width = 1190

export const generateBarChartSVG = async (req) => {
	let options = {
		filterTags: null,
		filterCategories: [],
		dateRange: [null, null],
		timePeriod: "months",
		width: chart_width,
		height: chart_height,
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
		const { incidentsByAllTime, xFormat, showByYears, allTime } = processIncidentsTimeData(filteredDataset, options.timePeriod);

		return ReactDOMServer.renderToString(
			<svg
				xmlns="http://www.w3.org/2000/svg"
				xmlnsXlink="http://www.w3.org/1999/xlink"
				version="1.1"
				width={options.width}
				height={options.height}
				viewBox={`0 0 ${options.width} ${options.height}`}
				style={{ fontFamily: "sans-serif" }}
			>
				<BarChart
					data={incidentsByAllTime}
					x={'date'}
					y={'count'}
					xFormat={xFormat}
					titleLabel={'incidents'}
					width={options.width}
					height={options.height}
					disableAnimation={true}
					isMobileView={false}
				/>
			</svg>
		)
	} catch (e) {
		console.error(e);
		return "<svg />";
	}
}

export const generateTreemapChartSVG = async (req) => {
	let options = {
		filterTags: null,
		filterCategories: [],
		dateRange: [null, null],
		branch: 'categories',
		width: chart_width,
		height: chart_height,
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
				width={options.width}
				height={options.height}
				viewBox={`0 0 ${options.width} ${options.height}`}
				style={{ fontFamily: "sans-serif" }}
			>
				<TreeMap
					data={filteredDataset}
					width={options.width}
					height={options.height}
					categoryColumn={'categories'}
					categoriesColors={categoriesColorMap}
					allCategories={Object.keys(categoriesColorMap)}
					minimumBarHeight={35}
					disableAnimation={true}
					interactive={false}
				/>
			</svg>
		)
	} catch (e) {
		console.error(e);
		return "<svg />";
	}
}

export const generateUSMapSVG = async (req) => {
	let options = {
		filterTags: null,
		filterCategories: [],
		dateRange: [null, null],
		aggregationLocality: 'state',
		width: chart_width,
		height: chart_height,
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
				width={options.width}
				height={options.height}
				viewBox={`0 0 ${options.width} ${options.height}`}
				style={{ fontFamily: "sans-serif" }}
			>
				<USMap
					data={datasetAggregatedByGeo}
					aggregationLocality={aggregationLocalityFnMap[options.aggregationLocality]}
					width={options.width}
					height={options.height}
					disableAnimation={true}
				/>
			</svg>
		)
	} catch (e) {
		console.error(e);
		return "<svg />";
	}
}
