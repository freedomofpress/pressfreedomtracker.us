import React from 'react'
import { createRoot } from 'react-dom/client'
import * as d3 from 'd3'
import CategoryPageChart from '../../charts/js/components/CategoryPageChart'
import DataLoader from '../../charts/js/components/DataLoader'

const fields = [
	'title',
	'date',
]

const chartContainers = Array.from(document.getElementsByClassName('js-categorypage-charts'))

chartContainers.forEach((node) => {
	const databasePath = node.dataset.databasePath
	const categoryName = node.dataset.categoryName
	const categoryId = parseInt(node.dataset.categoryId)
	const vizType = node.dataset.vizType
	const startDate = node.dataset.startDate
	const endDate = node.dataset.endDate

	const params = new URLSearchParams([
		['fields', fields.join(',')],
		['format', 'csv'],
		['categories', categoryId],
	])

	// If start or end date are set, limit the query to those dates
	if (startDate) params.append('date_lower', startDate)
	if (endDate) params.append('date_upper', endDate)

	const root = createRoot(node)
	root.render((
		<DataLoader
			dataUrl={[`/api/edge/incidents/?${params.toString()}`, '/api/edge/categories/']}
			dataKey={['data', 'categories']}
			dataParser={[(data) => d3.csvParse(data, d3.autoType), JSON.parse]}
			loadingComponent={false}
		>
			<CategoryPageChart
				data={[]}
				databasePath={databasePath}
				category={categoryId}
				categoryName={categoryName}
				vizType={vizType}
			/>
		</DataLoader>
	))
})
