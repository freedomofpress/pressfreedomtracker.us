import React from "react"
import { createRoot } from "react-dom/client"
import IncidentsTimeBarChart from './components/IncidentsTimeBarChart'
import DataLoader from "../../charts/js/components/DataLoader"
import * as d3 from 'd3'

function engageCharts() {
	const charts = document.querySelectorAll('.chart-vertical-bar:not(.engaged)')
	charts.forEach((chartNode) => {
		chartNode.classList.add('engaged')
		let root = createRoot(chartNode)
		const categoryKeys = Object.keys(chartNode.dataset || {}).filter(d => d.indexOf('category') === 0)
		const filterCategories = categoryKeys.map(k => chartNode.dataset[k]).filter(d => d)
		const filterTag = chartNode.dataset?.tag
		const lowerValue= chartNode.dataset?.lowerDate
		const upperValue = chartNode.dataset?.upperDate
		const timePeriod = chartNode.dataset?.timePeriod
		const title = chartNode.dataset?.title
		const description = chartNode.dataset?.description
		const interactive = !!chartNode.dataset?.interactive
		const fullSize = !!chartNode.dataset?.fullSize

		const filterUpperDate = upperValue ? new Date(upperValue) : null
		const filterLowerDate = lowerValue ? new Date(lowerValue) : null
		const url = chartNode.dataset.url

		let dataKey = ['dataset']
		let dataUrl = [url || '/api/edge/incidents/homepage_csv/?']
		let dataParser = [(data) => d3.csvParse(data, d3.autoType)]

		// Specifies if the tree map needs to be grouped, and the method and key
		// to group by
		const branchFieldName = chartNode.dataset.branchFieldName
		const branches = chartNode.dataset.branches && JSON.parse(chartNode.dataset.branches)
		const groupByTag = chartNode.dataset?.groupByTag
		let additionalProps = {}
		if (chartNode.dataset.branches && branches.type === 'list') {
			additionalProps.branches = branches.value
		} else if (chartNode.dataset.branches && branches.type === 'url') {
			dataUrl.push(branches.value)
			dataKey.push("branches")
			dataParser.push(JSON.parse)
		}

		root.render((
			<DataLoader
				dataUrl={dataUrl}
				dataKey={dataKey}
				dataParser={dataParser}
				loadingComponent={(
					<svg
						viewBox="0 0 655 440"
						width="100%"
						style={{ display: fullSize ? 'none' : 'block', backgroundColor: '#fafafa' }}
					/>
				)}
			>
				<IncidentsTimeBarChart
					filterCategories={filterCategories}
					filterTags={filterTag}
					dateRange={[filterLowerDate, filterUpperDate]}
					title={title}
					description={description}
					creditUrl={'pressfreedomtracker.us'}
					timePeriod={timePeriod}
					interactive={interactive}
					fullSize={fullSize}
					branchFieldName={branchFieldName}
					groupByTag={groupByTag}
					{...additionalProps}
				/>
			</DataLoader>
		))
	})
}

engageCharts();

// Add listener for query change to rerun
let previousUrl = '';

const observer = new MutationObserver(function(mutations) {
	if (window.location.href !== previousUrl) {
		previousUrl = window.location.href;
		engageCharts();
	}
});
const config = {subtree: true, childList: true};

// start listening to changes
observer.observe(document, config);
