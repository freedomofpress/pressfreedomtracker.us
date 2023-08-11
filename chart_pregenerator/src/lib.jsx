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

const generateFallbackSVG = (width, height) => `
	<svg
		xmlns="http://www.w3.org/2000/svg"
		xmlnsXlink="http://www.w3.org/1999/xlink"
		version="1.1"
		width="${width}"
		height="${height}"
	/>
`;

export const generateBarChartSVG = async (req) => {
	let options = {
		filterTags: null,
		filterCategories: [],
		dateRange: [null, null],
		branchFieldName: 'categories',
		branches: { type: "url", value: "/api/edge/categories/" },
		timePeriod: "months",
		width: chart_width,
		height: chart_height,
		mini: false,
	}

	try { options = {...options, ...JSON.parse(req.query.options)} }
	catch (e) { console.error(e) }

	let dataset, branches

	try {
		let dataKey = ['dataset']
		let dataUrl = [`${FPF_BASE_URL}/api/edge/incidents/?fields=tags%2Cdate%2Ccategories%2C${options.branchFieldName}&format=csv`]
		let dataParser = [(data) => d3.csvParse(data, d3.autoType)]

		if (options.branches && options.branches.type === 'url') {
			dataUrl.push(`${FPF_BASE_URL}${options.branches.value}`)
			dataKey.push("branches")
			dataParser.push(JSON.parse)
		}
		({ dataset, branches } = await loadData({ dataUrl, dataKey, dataParser, fetchFn: fetch }))
		branches = branches || options.branches?.value
	}	catch (e) { console.error(e) }

	if (!dataset) return generateFallbackSVG(options.width, options.height);

	try {
		// Filter down to the categories and tags and date range we want
		const filteredDataset = filterDatasets(dataset, options.filterCategories, options.filterTags, options.dateRange)
		const { incidentsByAllTime, xFormat } = processIncidentsTimeData(
			filteredDataset, options.timePeriod, options.branchFieldName
		);
		const categoriesColorMap = branches ? [...(new Set([...branches.map(d => d.title)]))]
			.reduce(
				(acc, category, i) => ({ ...acc, [category]: categoriesColors[i % categoriesColors.length] }),
				{}
			) : {}

		const Chart = options.mini ? BarChartMini : BarChart;

		return ReactDOMServer.renderToString(
			<svg
				xmlns="http://www.w3.org/2000/svg"
				xmlnsXlink="http://www.w3.org/1999/xlink"
				version="1.1"
				width={options.width}
				height={options.height}
				viewBox={`0 0 ${options.width} ${options.height}`}
				style={{ fontFamily: "Arial, sans-serif" }}
			>
				<Chart
					data={incidentsByAllTime}
					categoryColumn={options.branchFieldName}
					categoriesColors={categoriesColorMap}
					allCategories={Object.keys(categoriesColorMap)}
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
		return generateFallbackSVG(options.width, options.height);
	}
}

export const generateTreemapChartSVG = async (req) => {
	let options = {
		filterTags: null,
		filterCategories: [],
		dateRange: [null, null],
		branchFieldName: 'categories',
		branches: { type: "url", value: "/api/edge/categories/" },
		width: chart_width,
		height: chart_height,
		mini: false,
	}

	try { options = {...options, ...JSON.parse(req.query.options)} }
	catch (e) { console.error(e) }

	let dataset, branches

	try {
		let dataKey = ['dataset']
		let dataUrl = [`${FPF_BASE_URL}/api/edge/incidents/?fields=tags%2Cdate%2Ccategories%2C${options.branchFieldName}&format=csv`]
		let dataParser = [(data) => d3.csvParse(data, d3.autoType)]

		if (options.branches && options.branches.type === 'url') {
			dataUrl.push(`${FPF_BASE_URL}${options.branches.value}`)
			dataKey.push("branches")
			dataParser.push(JSON.parse)
		}
		({ dataset, branches } = await loadData({ dataUrl, dataKey, dataParser, fetchFn: fetch }))
		branches = branches || options.branches?.value
	} catch (e) { console.error(e) }

	if (!dataset) return generateFallbackSVG(options.width, options.height);

	try {
		// Filter down to the categories and tags and date range we want
		const filteredDataset = filterDatasets(dataset, options.filterCategories, options.filterTags, options.dateRange)
		const categoriesColorMap = branches ? [...(new Set([...branches.map(d => d.title)]))]
			.reduce(
				(acc, category, i) => ({ ...acc, [category]: categoriesColors[i % categoriesColors.length] }),
				{}
			) : {}

		const Chart = options.mini ? TreeMapMini : TreeMap;

		return ReactDOMServer.renderToString(
			<svg
				xmlns="http://www.w3.org/2000/svg"
				xmlnsXlink="http://www.w3.org/1999/xlink"
				version="1.1"
				width={options.width}
				height={options.height}
				viewBox={`0 0 ${options.width} ${options.height}`}
				style={{ fontFamily: "Arial, sans-serif" }}
			>
				<Chart
					data={filteredDataset}
					width={options.width}
					height={options.height}
					categoryColumn={options.branchFieldName}
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
		return generateFallbackSVG(options.width, options.height);
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
	catch (e) { console.error(e) }

	let dataset

	try {
		({ dataset } = await loadData({
			dataUrl: `${FPF_BASE_URL}/api/edge/incidents/homepage_csv/?`,
			dataKey: 'dataset',
			dataParser: (data) => d3.csvParse(data, d3.autoType),
			fetchFn: fetch
		}))
	} catch (e) { console.error(e) }

	if (!dataset) return generateFallbackSVG(options.width, options.height);

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
				style={{ fontFamily: "Arial, sans-serif" }}
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
		return generateFallbackSVG(options.width, options.height);
	}
}
