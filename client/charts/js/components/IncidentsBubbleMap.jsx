import React from 'react'
import {
	filterDatasets,
	groupByState,
	groupByCity,
	countIncidentsOutsideUS
} from '../lib/utilities'
import { ParentSize } from '@visx/responsive'
import ChartDownloader from './ChartDownloader'
import USMap from './USMap'

export default ({
	dataset,
	title,
	description,
	filterCategories = [], // Array of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	dateRange = [null, null], // Array representing the min and max of dates to show
	aggregationLocality = 'state', // Whether to group incidents by state or city
	isMobileView = false,
	creditUrl = '',
	categories
}) => {
	const aggregationLocalityMap = { state: groupByState, city: groupByCity }
	const aggregationLocalityFnMap = { state: d => d.state, city: d => `${d.city}, ${d.state}` }

	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange)
	const datasetAggregatedByGeo = filteredDataset && aggregationLocalityMap[aggregationLocality](filteredDataset)
	const incidentsOutsideUS = countIncidentsOutsideUS(filteredDataset)

	return (
		<ParentSize>
			{(parent) =>
				<ChartDownloader
					chartTitle={title}
					creditUrl={creditUrl}
					downloadFileName={title ? `${title}.png` : 'chart.png'}
				>
					<USMap
						data={datasetAggregatedByGeo}
						description={description}
						aggregationLocality={aggregationLocalityFnMap[aggregationLocality]}
						incidentsOutsideUS={incidentsOutsideUS}
						width={parent.width}
						height={parent.width * 0.7}
						overridePaddings={{ map: 0, bottom: 0 }}
					/>
				</ChartDownloader>
			}
		</ParentSize>
	)
}
