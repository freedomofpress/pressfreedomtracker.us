import React from 'react'
import { ParentSize } from '@visx/responsive'
import BarChart from './BarChart'
import BarChartMini from './BarChartMini'
import ChartDownloader from './ChartDownloader'
import * as d3 from 'd3'
import { categoriesColors, filterDatasets, tabletMinMainColumn } from '../lib/utilities'

export default function IncidentsTimeBarChart({
	dataset,
	title,
	description,
	filterCategories = [], // Array of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	dateRange = [null, null], // Array representing the min and max of dates to show
	timePeriod,
	isMobileView = false,
	creditUrl = '',
	interactive = true,
	fullSize = true,
	branchFieldName,
	branches,
	groupByTag,
}) {
	// Filter down to the categories and tags and date range we want
	const filteredDataset = filterDatasets(dataset, filterCategories, filterTags, dateRange)

	// if branchFieldName is set but branches is undefined, that means we are filtering a tag
	const tagBranches = (groupByTag)
		&& [{ title: groupByTag }, { title: `not ${groupByTag}` }];

	// Rollup the incidents
	const genIncidentsByTime = (dateFn) => filteredDataset.reduce((acc, d) => {
		const date = dateFn(d.date)

		const dateData = acc[date] || { count: 0 }
		dateData.count += 1

		if (groupByTag) {
			// if groupByTag is set, that means we are filtering a tag
			if (d.tags?.indexOf(groupByTag) >= 0) {
				dateData[groupByTag] = dateData[groupByTag] ? dateData[groupByTag] + 1 : 1
			} else {
				const notBranchFieldName = `not ${groupByTag}`;
				dateData[notBranchFieldName] = dateData[notBranchFieldName] ? dateData[notBranchFieldName] + 1 : 1
			}
		}
		else if (branchFieldName) {
			const branchValues = (d[branchFieldName] || "")
				.split(',')
				.map(e => e.trim())
				.filter(d => d)
			branchValues.forEach(branchName => {
				dateData[branchName] = dateData[branchName] ? dateData[branchName] + 1 : 1
			})
		}

		return ({ ...acc, [date]: dateData })
	}, {});
	const incidentsByMonth = genIncidentsByTime(d3.utcFormat('%Y-%m'))
	const incidentsByYear = genIncidentsByTime(d3.utcFormat('%Y'))

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
		// If this is the first item in the list, format with the year
		if (d3.utcFormat('%m-%Y')(date) === d3.utcFormat('%m-%Y')(allTime[0])
			|| d3.utcFormat('%m')(date) === '01') return d3.utcFormat("%Y")(date)
		// Format with the month abbreviation ie Jan, Feb, etc
		return d3.utcFormat("%b")(date)
	}

	// Make sure we have entries for months / years with no incidents
	const incidentsByAllTime = allTime
		.map((date) => ({ date, ...(incidentsByTime[timeFormat(date)] || { count: 0 }) }))
		.sort((a, b) => a.date - b.date)

	// Generate a default description for a11y
	const startYear = d3.utcFormat("%Y")(allTime[0])
	const endYear = d3.utcFormat("%Y")(allTime[allTime.length - 1])
	const dateDescription = (startYear === endYear) ? `in ${startYear}` : `from ${startYear} to ${endYear}`
	const generatedDescription = `Incidents ${dateDescription}`

	const categoriesColorMap = (tagBranches || branches ) &&
		[...(new Set([...(tagBranches || branches).map(d => d.title)]))]
			.reduce(
				(acc, category, i) => ({ ...acc, [category]: categoriesColors[i % categoriesColors.length] }),
				{}
			)

	return (
		<ParentSize>
			{(parent) => {
				const isMobile = parent.width ? parent.width < tabletMinMainColumn : isMobileView
				const barchart = fullSize ? (
					<BarChart
						description={description || generatedDescription}
						data={incidentsByAllTime}
						categoriesColors={categoriesColorMap}
						categoryColumn={branchFieldName}
						allCategories={categoriesColorMap && Object.keys(categoriesColorMap)}
						x={'date'}
						y={'count'}
						xFormat={xFormat}
						tooltipXFormat={d3.utcFormat(showByYears ? "%Y" : "%b %Y")}
						titleLabel={'incidents'}
						width={parent.width}
						height={Math.min(parent.width * (isMobile ? 1 : 0.75), 600) * (branchFieldName ? 1.2 : 1)}
						isMobileView={isMobile}
						interactive={interactive}
					/>
				) : (
					<BarChartMini
						data={incidentsByAllTime}
						categoriesColors={categoriesColorMap}
						allCategories={categoriesColorMap && Object.keys(categoriesColorMap)}
						x={'count'}
					/>
				);

				return interactive ? (
					<ChartDownloader
						chartTitle={title}
						creditUrl={creditUrl}
						downloadFileName={title ? `${title}.png` : 'chart.png'}
					>
						{barchart}
					</ChartDownloader>
				) : barchart
			}}
		</ParentSize>
	)
}
