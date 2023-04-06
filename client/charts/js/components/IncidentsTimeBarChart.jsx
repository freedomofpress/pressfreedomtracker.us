import React from 'react'
import BarChart from './BarChart'
import * as d3 from 'd3'

export default function IncidentsTimeBarChart({
	dataset,
	description = '',
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
	const filteredDataset = dataset
		.filter(({ categories = '', tags = '', date }) => {
			const incidentCategories = categories.split(',').map(d => d.trim())
			const incidentTags = tags.split(',').map(d => d.trim())

			const isExcludedCategory = filterCategories && !incidentCategories.find(c => filterCategoryMap[c])
			const isExcludedTag = filterTags && !incidentTags.find(c => filterTagsMap[c])

			const [startDate, endDate] = dateRange;
			if (startDate) startDate.setHours(0)
			if (endDate) endDate.setHours(0)
			const isBeforeStartDate = startDate && date < startDate
			const isAfterEndDate = endDate && date > endDate
			const isExcludedDate = isBeforeStartDate || isAfterEndDate

			return !isExcludedCategory && !isExcludedTag && !isExcludedDate
		})
		.map(({ date, ...restProps }) => {
			// Set the date to the start of the month
			date.setDate(1)
			date.setHours(0)
			return { ...restProps, date }
		})

	// Rollup the incidents by month-year
	const incidentsByMonth = Array.from(d3.rollup(filteredDataset, d => d.length, d => d.date))
		.reduce((acc, [date, count]) => ({ ...acc, [d3.timeFormat('%Y-%m')(date)]: count }), {})

	// Expand out all months
	const allMonths = [
		...d3.timeMonths(...d3.extent(filteredDataset, d => d.date)),
		// add in the last month entry because timeMonths excludes the final month
		d3.max(Object.keys(incidentsByMonth).map(d3.timeParse('%Y-%m')))
	].filter(d => d)

	// Make sure we have entries for months with no incidents
	const incidentsByAllMonths = allMonths
		.map((date) => ({ date, count: incidentsByMonth[d3.timeFormat('%Y-%m')(date)] || 0 }))
		.sort((a, b) => a.date - b.date)

	return (<BarChart
		description={description}
		data={incidentsByAllMonths}
		x={'date'}
		y={'count'}
		xFormat={d3.timeFormat('%Y-%m')}
		titleLabel={'incidents'}
		width={width}
		height={height}
		isMobileView={isMobileView}
	/>)
}
