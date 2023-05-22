import React from "react"
import { createRoot } from "react-dom/client"
import BubbleMapChart from './components/IncidentsBubbleMap'
import DataLoader from "../../charts/js/components/DataLoader"
import * as d3 from 'd3'

function engageCharts() {
	const charts = document.querySelectorAll('.chart-bubble-map')
	charts.forEach((chartNode) => {
		let root = createRoot(chartNode)
		const categoryKeys = Object.keys(chartNode.dataset || {}).filter(d => d.indexOf('category') === 0)
		const filterCategories = categoryKeys.map(k => chartNode.dataset[k])
		const filterTag = chartNode.dataset?.tag
		const lowerValue= chartNode.dataset?.lowerDate
		const upperValue = chartNode.dataset?.upperDate
		const groupBy = chartNode.dataset?.groupBy
		const title = chartNode.dataset?.title
		const description = chartNode.dataset?.description

		const filterUpperDate = upperValue ? new Date(upperValue) : null
		const filterLowerDate = lowerValue ? new Date(lowerValue) : null

		root.render((
			<DataLoader
				dataUrl={[`/api/edge/incidents/homepage_csv/?`]}
				dataKey={['dataset']}
				dataParser={[(data) => d3.csvParse(data, d3.autoType)]}
			>
				<BubbleMapChart
					filterCategories={filterCategories}
					filterTags={filterTag}
					dateRange={[filterLowerDate, filterUpperDate]}
					aggregationLocality={groupBy}
					title={title}
					description={description}
					creditUrl={chartNode.baseURI}
				/>
			</DataLoader>
		))
	})
}

engageCharts();