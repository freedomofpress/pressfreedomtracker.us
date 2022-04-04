import React, { useRef } from 'react'
import { ParentSize } from '@visx/responsive'
import TreeMap from './TreeMap'
import USMap from './USMap'
import BarChartHomepage from './BarChartHomepage'
import HomepageSelection from './HomepageSelection'
import Flashing from '../../../common/js/components/Flashing'
import {
	filterDatasetByFiltersApplied,
	groupByMonthSorted,
	monthIndexes,
	groupByState,
	countIncidentsOutsideUS,
	categoriesColors,
} from '../lib/utilities.js'

import '../../sass/HomepageMainCharts.sass'

const categoriesSlugs = {
	'Arrest/Criminal Charge': 'arrest-criminal-charge',
	'Border Stop': 'border-stop',
	'Subpoena/Legal Order': 'subpoena',
	'Leak Case': 'leak-case',
	'Equipment Search or Seizure': 'equipment-search-seizure-or-damage',
	'Physical Attack': 'physical-attack',
	'Denial of Access': 'denial-access',
	'Chilling Statement': 'chilling-statement',
	'Other Incident': 'other-incident',
	'Prior Restraint': 'prior-restraint',
	'Equipment Damage': 'equipment-damage',
}

function getFilteredUrl(databasePath, filtersApplied, currentDate) {
	const origin = window.location.origin
	const baseUrl = filtersApplied.category === undefined
		? `${origin}${databasePath}?`
		: `${origin}/${categoriesSlugs[filtersApplied.category]}/?`

	const parameters = []

	if (filtersApplied.monthName !== undefined) {
		const monthNumber = monthIndexes[filtersApplied.monthName]
		const year = !filtersApplied.sixMonths
			? filtersApplied.year
			: currentDate.getUTCMonth() > 6 || monthNumber <= 6
			? currentDate.getUTCFullYear()
			: currentDate.getUTCFullYear() - 1
		const paddedMonthNumber = String(monthNumber).padStart(2, '0')
		const firstDayMonth = `${year}-${paddedMonthNumber}-01`
		const lastDayMonth = `${year}-${paddedMonthNumber}-${new Date(year, monthNumber, 0).getDate()}`
		parameters.push(`date_lower=${firstDayMonth}&date_upper=${lastDayMonth}`)
	}

	if (filtersApplied.state !== undefined) {
		parameters.push(`state=${filtersApplied.state.replace(' ', '+')}`)
	}

	if (filtersApplied.year !== null && filtersApplied.monthName === undefined) {
		parameters.push(`date_lower=${filtersApplied.year}-01-01&date_upper=${filtersApplied.year}-12-31`)
	}

	if (filtersApplied.sixMonths && filtersApplied.monthName === undefined) {
		const currentMonth = currentDate.getUTCMonth()
		const currentYear = currentDate.getUTCFullYear()

		const lastDate = new Date(currentYear, currentMonth + 1, 0)  // last day of the current month
		const firstDate = new Date(currentYear, currentMonth - 5, 1)  // first day of the month five months ago
		const firstDateFormatted = firstDate.toISOString().substring(0, 10)  // Extract the date portion of the ISO datetime
		const lastDateFormatted = lastDate.toISOString().substring(0, 10)

		parameters.push(`date_lower=${firstDateFormatted}&date_upper=${lastDateFormatted}`)
	}

	if (filtersApplied.tag !== null) {
		parameters.push(`tags=${filtersApplied.tag.replace(' ', '-')}`)
	}

	return `${baseUrl}${parameters.join('&')}`
}

function goToFilterPage(databasePath, filtersApplied, currentDate) {
	const url = getFilteredUrl(databasePath, filtersApplied, currentDate)
	window.location = url
}

export default function HomepageMainCharts(props) {
	return (
		<ParentSize>
			{(parent) => <HomepageMainChartsWidth {...props} width={parent.width} />}
		</ParentSize>
	)
}

function HomepageMainChartsWidth({
	data: dataset,
	width,
	currentDate = new Date(),
	selectedTags = [],
	databasePath = '/',
	loading = false,
}) {
	const [filtersApplied, setFiltersApplied] = React.useState({
		tag: null,
		year: null,
		sixMonths: true,
	})

	const chartWidth = width > 970 ? width / 3 : width
	const chartHeight = width > 970 ? 500 : 480

	const datasetFiltered = filterDatasetByFiltersApplied(dataset, filtersApplied, currentDate)

	const datasetAggregatedByGeo = groupByState(datasetFiltered)
	const incidentsOutsideUS = countIncidentsOutsideUS(datasetFiltered)

	const datasetGroupedByMonth = groupByMonthSorted(
		datasetFiltered,
		filtersApplied.sixMonths,
		currentDate
	)

	return (
		<Flashing flashing={loading}>
			<HomepageSelection
				width={width}
				height={'40px'}
				data={dataset}
				numberOfTags={5}
				filtersApplied={filtersApplied}
				setFiltersApplied={setFiltersApplied}
				selectedTags={selectedTags}
			/>

			<div className={'hpChartContainer'} style={{ width: width }}>
				<div className={'hpChart'}>
					<ChartDescription>
						Showing incidents grouped by type of attack. An incident can fall under more than one
						category.
					</ChartDescription>
					<TreeMap
						data={datasetFiltered}
						width={chartWidth}
						height={chartHeight}
						isHomePageDesktopView={width > 970}
						minimumBarHeight={35}
						categoryColumn={'categories'}
						titleLabel={'incidents'}
						openSearchPage={(category) => {
							goToFilterPage(databasePath, { ...filtersApplied, category }, currentDate)
						}}
						allCategories={Object.keys(categoriesColors)}
					/>
				</div>
				<div className={'hpChart'}>
					<ChartDescription>
						Showing incidents distribution in the U.S. Incidents are grouped by state.
					</ChartDescription>
					<USMap
						data={datasetAggregatedByGeo}
						incidentsOutsideUS={incidentsOutsideUS}
						width={chartWidth}
						height={chartHeight}
						openSearchPage={(state) => {
							goToFilterPage(databasePath, { ...filtersApplied, state }, currentDate)
						}}
					/>
				</div>
				<div className={'hpChart'}>
					<ChartDescription>Showing the number of journalists targeted per month.</ChartDescription>
					<BarChartHomepage
						data={datasetGroupedByMonth}
						x={'monthName'}
						y={'numberOfIncidents'}
						titleLabel={'incidents'}
						width={chartWidth}
						height={chartHeight}
						isMobileView={width < 970}
						openSearchPage={(monthName) => {
							goToFilterPage(databasePath, { ...filtersApplied, monthName }, currentDate)
						}}
					/>
				</div>
			</div>
		</Flashing>
	)
}

function ChartDescription({ children }) {
	return (
		<div
			style={{
				height: '2em',
				padding: 10,
				fontFamily: 'var(--font-base)',
				fontWeight: 400,
				fontSize: 14,
				color: '#7A848E',
				marginBottom: '1rem'
			}}
		>
			{children}
		</div>
	)
}
