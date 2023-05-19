import React from 'react'
import { ParentSize } from '@visx/responsive'
import BarChart from './BarChart'
import ChartDownloader from './ChartDownloader'
import * as d3 from 'd3'
import { filterDatasets } from '../lib/utilities'

export default function IncidentsTimeBarChart({
	dataset,
	title,
	description,
	filterCategories = null, // Array or string of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	dateRange = [null, null], // Array representing the min and max of dates to show
	timePeriod,
	isMobileView = false,
	creditUrl = ''
}) {
	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange)

	// Rollup the incidents by month-year
	const incidentsByMonth = Array
		.from(d3.rollup(filteredDataset, d => d.length, d => d3.utcFormat('%Y-%m')(d.date)))
		.reduce((acc, [date, count]) => ({ ...acc, [date]: count }), {})
	const incidentsByYear = Array
		.from(d3.rollup(filteredDataset, d => d.length, d => d3.utcFormat('%Y')(d.date)))
		.reduce((acc, [date, count]) => ({ ...acc, [date]: count }), {})

	// If the dataset we are working with spans >24 months then automatically switch to year
	const showByYears = timePeriod ? timePeriod === 'years' : Object.keys(incidentsByMonth).length > 24
	const timeIntervalFn = showByYears ? d3.utcYears : d3.utcMonths
	const incidentsByTime = showByYears ? incidentsByYear : incidentsByMonth
	const timeFormat = showByYears ? d3.utcFormat('%Y') : d3.utcFormat('%Y-%m')

	// Expand out all months
	const allTime = [
		...timeIntervalFn(...d3.extent(
			filteredDataset.map(({ date, ...restProps }) => ({
				...restProps, date: showByYears ? d3.utcYear.floor(date) : date
			})),
			d => d.date
		)),
		// add in the last "time" entry because utcMonths / utcYears excludes the final month / year
		d3.max(Object.keys(incidentsByTime).map(d3.utcParse(showByYears ? '%Y' : '%Y-%m')))
	].filter(d => d)

	const xFormat = (date) => {
		if (showByYears) return timeFormat(date)
		if (Object.keys(incidentsByYear).length === 1) return d3.utcFormat("%b")(date)
		if (d3.utcFormat('%m-%Y')(date) === d3.utcFormat('%m-%Y')(allTime[0])
			|| d3.utcFormat('%m')(date) === '01') return d3.utcFormat("%Y")(date)
		return d3.utcFormat("%b")(date)
	}

	// Make sure we have entries for months / years with no incidents
	const incidentsByAllTime = allTime
		.map((date) => ({ date, count: incidentsByTime[timeFormat(date)] || 0 }))
		.sort((a, b) => a.date - b.date)

	// Generate a default description for a11y
	const startYear = d3.utcFormat("%Y")(allTime[0])
	const endYear = d3.utcFormat("%Y")(allTime[allTime.length - 1])
	const dateDescription = (startYear === endYear) ? `in ${startYear}` : `from ${startYear} to ${endYear}`
	const generatedDescription = `Incidents ${dateDescription}`

	return (
		<ParentSize>
			{(parent) =>
				<ChartDownloader
					chartTitle={title}
					creditUrl={creditUrl}
					downloadFileName={title ? `${title}.png` : 'chart.png'}
				>
					<BarChart
						description={description || generatedDescription}
						data={incidentsByAllTime}
						x={'date'}
						y={'count'}
						xFormat={xFormat}
						tooltipXFormat={d3.utcFormat(showByYears ? "%Y" : "%b %Y")}
						titleLabel={'incidents'}
						width={parent.width}
						height={parent.width * 0.75}
						isMobileView={isMobileView}
					/>
				</ChartDownloader>
			}
		</ParentSize>
	)
}
