import React from 'react'
import BarChart from './BarChart'
import * as d3 from 'd3'

export default function IncidentsTimeBarChart({
	dataset,
	filterCategories = null, // Array or string of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	dateRange = null, // Array representing the min and max of dates to show
	width = 800,
	height = 500,
	isMobileView = false,
}) {
	// Create maps so that we don't have to do n^2 lookup times
	const filterCategoryMap = (Array.isArray(filterCategories) ? filterCategories : [filterCategories])
		.reduce((acc, val) => ({...acc, [val]: true}), {})
	const filterTagsMap = (Array.isArray(filterTags) ? filterTags : [filterTags])
		.reduce((acc, val) => ({...acc, [val]: true}), {})

	// Filter down to the categories and tags and date range we want
	const filteredDataset = dataset.filter(({ categories = '', tags = '', date }) => {
		const incidentCategories = categories.split(',').map(d => d.trim())
		const incidentTags = tags.split(',').map(d => d.trim())

		const isExcludedCategory = filterCategories && !incidentCategories.find(c => filterCategoryMap[c])
		const isExcludedTag = filterTags && !incidentTags.find(c => filterTagsMap[c])
		const isExcludedDate = dateRange?.length === 2 && (date < dateRange[0] || date > dateRange[1])

		return !isExcludedCategory && !isExcludedTag && !isExcludedDate
	})

	// Reduce the incidents by month-year
	const incidentsByMonth = Array.from(d3.rollup(
		filteredDataset, d => d.length, d => d3.timeFormat('%Y-%m')(d.date)
	))
		.map(([date, count]) => ({ date: d3.timeParse('%Y-%m')(date), count }))
		.sort((a, b) => a.date - b.date)

	// Expand out all months that have no data
	const expandedMonths = d3.timeMonths(...d3.extent(incidentsByMonth, d => d.date))
	if (incidentsByMonth.length > 0) {
		const lastMonth = incidentsByMonth[incidentsByMonth.length - 1].date
		lastMonth.setMonth(lastMonth.getMonth() + 1)
		expandedMonths.push(lastMonth)
	}

	return (<BarChart
		data={incidentsByMonth}
		x={'date'}
		y={'count'}
		xFormat={(date) => d3.timeFormat('%Y-%m')(date)}
		xDomain={expandedMonths}
		titleLabel={'incidents'}
		width={width}
		height={height}
		isMobileView={isMobileView}
	/>)
}
