import React from "react"
import { createRoot } from "react-dom/client"
import IncidentsTimeBarChart from './components/IncidentsTimeBarChart'
import DataLoader from "../../charts/js/components/DataLoader"

function engageCharts() {
	const charts = document.querySelectorAll('.chart-vertical-bar')
	charts.forEach((chartNode) => {
		let root = createRoot(chartNode)
		const filterCategory = chartNode.dataset?.category
		const filterTag = chartNode.dataset?.tag
		const lowerValue= chartNode.dataset?.lowerDate
		const upperValue = chartNode.dataset?.upperDate
		const title = chartNode.dataset?.title
		const description = chartNode.dataset?.description
		const url = chartNode.dataset?.url

		const filterUpperDate = upperValue ? new Date(upperValue) : null
		const filterLowerDate = lowerValue ? new Date(lowerValue) : null

		root.render((
			<DataLoader
				dataUrl={`/api/edge/incidents/homepage_csv/?`}
				dataKey="dataset"
			>
				<IncidentsTimeBarChart
					filterCategories={filterCategory}
					filterTags={filterTag}
					dateRange={[filterLowerDate, filterUpperDate]}
					title={title}
					description={description}
					creditUrl={url || chartNode.baseURI}
				/>
			</DataLoader>
		))
	})
}

engageCharts();
