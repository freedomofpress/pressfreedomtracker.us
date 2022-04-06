import React from "react"
import ReactDOM from "react-dom"

import HomepageMainCharts from '../../charts/js/components/HomepageMainCharts'
import DataLoader from "../../charts/js/components/DataLoader"
import Flashing from './components/Flashing'

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

	const params = new URLSearchParams([
		['fields', fields.join(',')],
		['format', 'csv'],
	])

	// If start or end date are set, limit the query to those dates
	if (startDate) params.append('date_lower', startDate)
	if (endDate) params.append('date_upper', endDate)

	ReactDOM.render((
		<DataLoader
			dataUrl={`/api/edge/incidents/?${params.toString()}`}
			loadingComponent={(
				<HomepageMainCharts selectedTags={selectedTags} databasePath={databasePath} data={[]} loading={true} />
			)}
		>
			<HomepageMainCharts selectedTags={selectedTags} databasePath={databasePath} />
		</DataLoader>
	), node)
})
