import React from 'react'
import { createRoot } from 'react-dom/client'

import * as d3 from 'd3'
import HomepageMainCharts from '../../charts/js/components/HomepageMainCharts'
import DataLoader from '../../charts/js/components/DataLoader'

const fields = [
	'categories',
	'authors',
	'date',
	'city',
	'state',
	'latitude',
	'longitude',
	'tags',
]

const chartContainers = Array.from(document.getElementsByClassName('js-homepage-charts'))

chartContainers.forEach((node) => {
	const selectedTags = JSON.parse(node.dataset.tags)
	const databasePath = node.dataset.databasePath
	const startDate = node.dataset.startDate
	const endDate = node.dataset.endDate
	// TODO: add admin controls to add this attr when enabled
	const sevenDayEnabled = node.dataset.sevenDayEnabled === 'true'

	const params = new URLSearchParams([
		['fields', fields.join(',')],
		['format', 'csv'],
	])

	// If start or end date are set, limit the query to those dates
	if (startDate) params.append('date_lower', startDate)
	if (endDate) params.append('date_upper', endDate)

	const root = createRoot(node)
	root.render((
		<DataLoader
			dataUrl={[`/api/edge/incidents/homepage_csv/?${params.toString()}`, '/api/edge/categories/']}
			dataKey={['data', 'categories']}
			dataParser={[(data) => d3.csvParse(data, d3.autoType), JSON.parse]}
			loadingComponent={false}
		>
			<HomepageMainCharts
				data={[]}
				selectedTags={selectedTags}
				databasePath={databasePath}
				sevenDayEnabled={sevenDayEnabled}
			/>
		</DataLoader>
	))
})
