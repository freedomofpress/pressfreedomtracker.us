import React from 'react'
import { ParentSize } from '@visx/responsive'
import TreeMap from './TreeMap'
import HexbinUSMap from './HexbinUSMap'
import BarChart from './BarChart'
import HomepageSelection from './HomepageSelection'
import ChartDescription from "./ChartDescription"
import Flashing from '../../../common/js/components/Flashing'
import {
	filterDatasetByFiltersApplied,
	resolveDefaultTimePreset,
	groupByMonthSorted,
	groupByYearsSorted,
	groupByDaysSorted,
	groupByWeeksSorted,
	groupByState,
	countIncidentsOutsideUS,
	categoriesColors,
	getFilteredUrl,
	TIME_PRESETS,
} from '../lib/utilities.js'

import '../../sass/HomepageMainCharts.sass'

export default function HomepageMainCharts(props) {
	return (
		<ParentSize debounceTime={0}>
			{(parent) => <HomepageMainChartsWidth {...props} width={parent.width} />}
		</ParentSize>
	)
}

const mobileBreakpoint = 950

const CHART_DESCRIPTIONS = {
	[TIME_PRESETS.SEVEN_DAYS]: 'Showing the number of journalists targeted per day.',
	[TIME_PRESETS.FOUR_WEEKS]: 'Showing the number of journalists targeted per week. (Monday–Sunday weeks.)',
	[TIME_PRESETS.TWELVE_WEEKS]: 'Showing the number of journalists targeted per week. (Monday–Sunday weeks.)',
}
const DEFAULT_CHART_DESCRIPTION = 'Showing the number of journalists targeted per month.'

function HomepageMainChartsWidth({
	data: dataset,
	width,
	currentDate = new Date(),
	selectedTags = [],
	databasePath = '/',
	loading = false,
	categories = [],
	sevenDayEnabled = false,
}) {
	// timePreset is determined by resolveDefaultTimePreset until the user chooses otherwise
	const [filterSelection, setFiltersApplied] = React.useState({
		tag: null,
		year: null,
		timePreset: null,
	})

	const filtersApplied = {
		...filterSelection,
		timePreset: filterSelection.timePreset
			?? resolveDefaultTimePreset(dataset, currentDate, sevenDayEnabled),
	}

	const categoriesColorMap = categories.reduce(
		(acc, { title }, i) => ({ ...acc, [title]: categoriesColors[i % categoriesColors.length] }),
		{}
	)

	const chartWidth = width > mobileBreakpoint ? width / 3 : width
	const chartHeight = width > mobileBreakpoint ? 500 : 480

	const datasetFiltered = filterDatasetByFiltersApplied(dataset, filtersApplied, currentDate)
	const datasetAggregatedByGeo = groupByState(datasetFiltered)
	const incidentsOutsideUS = countIncidentsOutsideUS(datasetFiltered)

	const barChartProps = {
		y: 'numberOfIncidents',
		titleLabel: 'incidents',
		id: 'homepage-bar-chart-label',
		width: chartWidth,
		height: chartHeight,
		isMobileView: width < mobileBreakpoint,
	}

	const isWeekView = filtersApplied.timePreset === TIME_PRESETS.FOUR_WEEKS
		|| filtersApplied.timePreset === TIME_PRESETS.TWELVE_WEEKS

	// Pick bucket size for bars (day/month/year), format label, and decide what each bar links to
	switch (filtersApplied.timePreset) {
		case TIME_PRESETS.SEVEN_DAYS: {
			const dayData = groupByDaysSorted(datasetFiltered, currentDate, 7)
			const dayByLabel = Object.fromEntries(dayData.map((d) => [d.label, d]))
			barChartProps.data = dayData
			barChartProps.x = 'label'
			barChartProps.tooltipXFormat = (label) => dayByLabel[label]?.range ?? label
			barChartProps.searchPageURL = (label) => {
				const day = dayByLabel[label]
				if (!day) return null
				return getFilteredUrl(
					databasePath,
					{ ...filtersApplied, weekStart: day.date, weekEnd: day.date },
					currentDate,
					categories,
				)
			}
			break
		}
		case TIME_PRESETS.FOUR_WEEKS:
		case TIME_PRESETS.TWELVE_WEEKS: {
			const numberOfWeeks = filtersApplied.timePreset === TIME_PRESETS.FOUR_WEEKS ? 4 : 12
			const weekData = groupByWeeksSorted(datasetFiltered, currentDate, numberOfWeeks)
			const weekByLabel = Object.fromEntries(weekData.map((w) => [w.label, w]))
			barChartProps.data = weekData
			barChartProps.x = 'label'
			barChartProps.tooltipXFormat = (label) => weekByLabel[label]?.range ?? label
			barChartProps.searchPageURL = (label) => {
				const week = weekByLabel[label]
				if (!week) return null
				return getFilteredUrl(
					databasePath,
					{ ...filtersApplied, weekStart: week.weekStart, weekEnd: week.weekEnd },
					currentDate,
					categories,
				)
			}
			break
		}
		case TIME_PRESETS.ALL_TIME: {
			barChartProps.data = groupByYearsSorted(datasetFiltered)
			barChartProps.x = 'year'
			barChartProps.searchPageURL = (year) => getFilteredUrl(databasePath, { ...filtersApplied, year, timePreset: TIME_PRESETS.YEAR }, currentDate, categories)
			break
		}
		case TIME_PRESETS.SIX_MONTHS:
		case TIME_PRESETS.YEAR: {
			barChartProps.x = 'monthName'
			barChartProps.data = groupByMonthSorted(
				datasetFiltered,
				filtersApplied.timePreset === TIME_PRESETS.SIX_MONTHS,
				currentDate,
			)
			barChartProps.searchPageURL = (monthName) => getFilteredUrl(databasePath, { ...filtersApplied, monthName }, currentDate, categories)
			break
		}
	}

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
				sevenDayEnabled={sevenDayEnabled}
			/>

			<div className={'hpChartContainer'} style={{ width: width }}>
				<div className={'hpChart'}>
					<ChartDescription id={'homepage-treemap-chart-label'}>
						Showing incidents grouped by type of attack. An incident can fall under more than one
						category.
					</ChartDescription>
					<TreeMap
						data={datasetFiltered}
						width={chartWidth}
						height={chartHeight}
						id={'homepage-treemap-chart-label'}
						isHomePageDesktopView={width > mobileBreakpoint}
						minimumBarHeight={35}
						categoryColumn={'categories'}
						titleLabel={'incidents'}
						searchPageURL={(category) =>
							getFilteredUrl(databasePath, { category }, currentDate, categories)
						}
						categoriesColors={categoriesColorMap}
						allCategories={Object.keys(categoriesColorMap)}
					/>
				</div>
				<div className={'hpChart'}>
					<ChartDescription id={'homepage-usmap-chart-label'}>
						Showing incidents distribution in the U.S. Incidents are grouped by state.
					</ChartDescription>
					<HexbinUSMap
						data={datasetAggregatedByGeo}
						incidentsOutsideUS={incidentsOutsideUS}
						width={chartWidth}
						height={chartHeight}
						id={'homepage-usmap-chart-label'}
						searchPageURL={(state) =>
							getFilteredUrl(databasePath, { ...filtersApplied, state }, currentDate, categories)
						}
						addBottomBorder={true}
					/>
				</div>
				<div className={'hpChart'}>
					<ChartDescription id={'homepage-bar-chart-label'}>
						{CHART_DESCRIPTIONS[filtersApplied.timePreset] ?? DEFAULT_CHART_DESCRIPTION}
					</ChartDescription>
					<BarChart {...barChartProps} />
					{isWeekView && width > mobileBreakpoint && (
						<div className='hpBarChartAxisLabel'>Week beginning on</div>
					)}
				</div>
			</div>
		</Flashing>
	)
}
