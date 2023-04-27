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
	isMobileView = false,
	creditUrl = ''
}) {
	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange)

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
						tooltipXFormat={d3.timeFormat("%b %Y")}
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
