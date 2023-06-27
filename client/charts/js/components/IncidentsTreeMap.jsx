import React from 'react'
import { filterDatasets, categoriesColors } from '../lib/utilities'
import { ParentSize } from '@visx/responsive'
import ChartDownloader from './ChartDownloader'
import TreeMap from './TreeMap'
import TreeMapMini from './TreeMapMini'

export default ({
	dataset,
	title,
	description,
	filterCategories = [], // Array of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	dateRange = [null, null], // Array representing the min and max of dates to show
	isMobileView = false,
	creditUrl = '',
	branchFieldName,
	categories,
	branches,
	interactive = true,
	fullSize = true,
}) => {
	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange)

	const categoriesColorMap = [...(new Set([...branches.map(d => d.title)]))]
		.reduce(
			(acc, category, i) => ({ ...acc, [category]: categoriesColors[i % categoriesColors.length] }),
			{}
		)

	return (
		<ParentSize>
			{(parent) => {
				const treemap = fullSize ? (
						<TreeMap
							data={filteredDataset}
							categoryColumn={branchFieldName}
							description={description}
							titleLabel={'incidents'}
							width={parent.width}
							height={Math.min(parent.width * 0.75, 600)}
							isMobileView={isMobileView}
							categoriesColors={categoriesColorMap}
							allCategories={Object.keys(categoriesColorMap)}
							minimumBarHeight={35}
							interactive={interactive}
						/>
					) : (
						<TreeMapMini
							data={filteredDataset}
							categoryColumn={branchFieldName}
							categoriesColors={categoriesColorMap}
						 	allCategories={Object.keys(categoriesColorMap)}
						/>
				)
				return interactive ? (
					<ChartDownloader
						chartTitle={title}
						creditUrl={creditUrl}
						downloadFileName={title ? `${title}.png` : 'chart.png'}
					>
						{treemap}
					</ChartDownloader>
				) : treemap
			}}
		</ParentSize>
	)
}
