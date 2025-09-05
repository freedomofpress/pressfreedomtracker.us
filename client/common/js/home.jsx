import React, { useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'

import * as d3 from 'd3'
import HomepageMainCharts from '../../charts/js/components/HomepageMainCharts'
// import DataLoader from '../../charts/js/components/DataLoader'

// const fields = [
// 	'categories',
// 	'authors',
// 	'date',
// 	'city',
// 	'state',
// 	'latitude',
// 	'longitude',
// 	'tags',
// ]

// TEMP Load from CSV
import { csv } from '../../charts/js/data/incidents.csv.js'
function CSVHomepageCharts({ selectedTags, databasePath }) {
	const [dataset, setDataset] = useState(null)
	const [categories, setCategories] = useState([])

	useEffect(() => {
		try {
			const parsedData = d3.csvParse(csv, d3.autoType)
			setDataset(parsedData)
		} catch (err) {
			console.error('Error parsing CSV:', err)
			setDataset([])
		}

		fetch('/api/edge/categories/')
			.then(response => response.json())
			.then(data => setCategories(data))
			.catch(err => {
				console.error('Error loading categories:', err)
				setCategories([])
			})
	}, [])

	if (dataset === null) {
		return <div>Loading...</div>
	}

	return <HomepageMainCharts data={dataset} selectedTags={selectedTags} databasePath={databasePath} categories={categories} />
}
// TEMP: load from csv

const chartContainers = Array.from(document.getElementsByClassName('js-homepage-charts'))

chartContainers.forEach((node) => {
	const selectedTags = JSON.parse(node.dataset.tags)
	const databasePath = node.dataset.databasePath
	// const startDate = node.dataset.startDate
	// const endDate = node.dataset.endDate

	// const params = new URLSearchParams([
	// 	['fields', fields.join(',')],
	// 	['format', 'csv'],
	// ])

	// // If start or end date are set, limit the query to those dates
	// if (startDate) params.append('date_lower', startDate)
	// if (endDate) params.append('date_upper', endDate)


	const root = createRoot(node)
	// 	root.render((
	// 	<DataLoader
	// 		dataUrl={[`/api/edge/incidents/homepage_csv/?${params.toString()}`, '/api/edge/categories/']}
	// 		dataKey={['data', 'categories']}
	// 		dataParser={[(data) => d3.csvParse(data, d3.autoType), JSON.parse]}
	// 		loadingComponent={false}
	// 	>
	// 		<HomepageMainCharts data={[]} selectedTags={selectedTags} databasePath={databasePath} />
	// 	</DataLoader>
	// ))

	// TEMP: Load from CSV
	root.render(<CSVHomepageCharts selectedTags={selectedTags} databasePath={databasePath} />)
	// TEMP: End load from CSV
})
