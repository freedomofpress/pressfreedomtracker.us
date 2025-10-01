import React from 'react'
import {
	filterDatasets,
	groupByState,
	countIncidentsOutsideUS,
} from '../lib/utilities'
import { ParentSize } from '@visx/responsive'
import ChartDownloader from './ChartDownloader'
import HexbinUSMap from './HexbinUSMap'

export default ({
	dataset,
	title,
	description,
	filterCategories = [], // Array of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	filterStates = new Set(),
	dateRange = [null, null], // Array representing the min and max of dates to show
	creditUrl = '',
	interactive = true,
	fullSize,
}) => {
	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange, filterStates)
	const datasetAggregatedByGeo = filteredDataset && groupByState(filteredDataset) // Hexbin maps are always state-level
	const incidentsOutsideUS = countIncidentsOutsideUS(filteredDataset)

	return (
		<ParentSize>
			{(parent) => {
				const usmap = (
					<HexbinUSMap
						data={datasetAggregatedByGeo}
						description={description}
						aggregationLocality={d => d.state}
						incidentsOutsideUS={incidentsOutsideUS}
						width={fullSize ? parent.width : 655}
						height={fullSize ? (parent.width * 0.7) : 440}
						overridePaddings={{ map: 0, bottom: 0 }}
						interactive={interactive}
						fullSize={fullSize}
						id="hexbin-map-chart"
					/>
				);

				return interactive ? (
					<ChartDownloader
						chartTitle={title}
						creditUrl={creditUrl}
						downloadFileName={title ? `${title}.png` : 'chart.png'}
					>
						{usmap}
					</ChartDownloader>
				) : usmap
			}}
		</ParentSize>
	)
}
