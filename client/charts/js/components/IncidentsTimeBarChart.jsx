import React from 'react'
import BarChart from './BarChart'
import * as d3 from 'd3'

export default function IncidentsTimeBarChart({
	dataset,
	description,
	filterCategories = null, // Array or string of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	dateRange = [null, null], // Array representing the min and max of dates to show
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
	const incidentsByYear = Array.from(d3.rollup(filteredDataset, d => d.length, d => d.date))
		.reduce((acc, [date, count]) => ({ ...acc, [d3.timeFormat('%Y')(date)]: count }), {})

	// If the dataset we are working with spans >24 months then automatically switch to year
	const spansMoreThanTwoYears = Object.keys(incidentsByMonth).length > 24
	const timeIntervalFn = spansMoreThanTwoYears ? d3.timeYears : d3.timeMonths
	const incidentsByTime = spansMoreThanTwoYears ? incidentsByYear : incidentsByMonth
	const timeFormat = spansMoreThanTwoYears ? d3.timeFormat('%Y') : d3.timeFormat('%Y-%m')

	// Expand out all months
	const allTime = [
		...timeIntervalFn(...d3.extent(filteredDataset, d => d.date)),
		// add in the last "time" entry because timeMonths / timeYears excludes the final month / year
		d3.max(Object.keys(incidentsByTime).map(d3.timeParse('%Y-%m')))
	].filter(d => d)

	const xFormat = (date) => {
		if (spansMoreThanTwoYears) return timeFormat(date)
		if (Object.keys(incidentsByYear).length === 1) return d3.timeFormat("%b")(date)
		if (d3.timeFormat('%m-%Y')(date) === d3.timeFormat('%m-%Y')(allTime[0])
			|| d3.timeFormat('%m')(date) === '01') return d3.timeFormat("%Y")(date)
		return d3.timeFormat("%b")(date)
	}

	// Make sure we have entries for months / years with no incidents
	const incidentsByAllTime = allTime
		.map((date) => ({ date, count: incidentsByTime[timeFormat(date)] || 0 }))
		.sort((a, b) => a.date - b.date)

	// Generate a default description for a11y
	const startYear = d3.timeFormat("%Y")(allTime[0])
	const endYear = d3.timeFormat("%Y")(allTime[allTime.length - 1])
	const dateDescription = (startYear === endYear) ? `in ${startYear}` : `from ${startYear} to ${endYear}`
	const generatedDescription = `Incidents ${dateDescription}`

	return (<BarChart
		description={description || generatedDescription}
		data={incidentsByAllTime}
		x={'date'}
		y={'count'}
		xFormat={xFormat}
		tooltipXFormat={d3.timeFormat("%b %Y")}
		titleLabel={'incidents'}
		width={width}
		height={height}
		isMobileView={isMobileView}
	/>)
}
