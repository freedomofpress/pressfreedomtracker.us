import React from 'react'
import { filterDatasets, categoriesColors } from '../lib/utilities'
import { ParentSize } from '@visx/responsive'
import ChartDownloader from './ChartDownloader'
import TreeMap from './TreeMap'

export default ({
	dataset,
	title,
	description,
	filterCategories = null, // Array or string of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	dateRange = [null, null], // Array representing the min and max of dates to show
	isMobileView = false,
	creditUrl = '',
	categories
}) => {
	// Remove empty strings from filterCategories
	let filteredFilterCategories = filterCategories.filter(d => d)
	filteredFilterCategories = filteredFilterCategories.length ? filteredFilterCategories : null

	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filteredFilterCategories, filterTags, dateRange)

	const categoriesColorMap = [...(new Set([...filterCategories, ...categories.map(d => d.title)]))]
		.reduce(
			(acc, category, i) => ({ ...acc, [category]: categoriesColors[i % categoriesColors.length] }),
			{}
		)

	return (
		<ParentSize>
			{(parent) =>
				<ChartDownloader
					chartTitle={title}
					creditUrl={creditUrl}
					downloadFileName={title ? `${title}.png` : 'chart.png'}
				>
					<TreeMap
						data={filteredDataset}
						categoryColumn="categories"
						description={description}
						titleLabel={'incidents'}
						width={parent.width}
						height={parent.width * 0.75}
						isMobileView={isMobileView}
						categoriesColors={categoriesColorMap}
						allCategories={Object.keys(categoriesColorMap)}
						minimumBarHeight={35}
					/>
				</ChartDownloader>
			}
		</ParentSize>
	)
}