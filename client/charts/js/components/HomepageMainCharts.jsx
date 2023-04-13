import React, { useRef } from 'react'
import { ParentSize } from '@visx/responsive'
import TreeMap from './TreeMap'
import USMap from './USMap'
import BarChart from './BarChart'
import HomepageSelection from './HomepageSelection'
import ChartDescription from "./ChartDescription"
import Flashing from '../../../common/js/components/Flashing'
import {
	filterDatasetByFiltersApplied,
	groupByMonthSorted,
	groupByState,
	goToFilterPage,
	countIncidentsOutsideUS,
	categoriesColors,
} from '../lib/utilities.js'

import '../../sass/HomepageMainCharts.sass'

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
	categories = [],
}) {
	const [filtersApplied, setFiltersApplied] = React.useState({
		tag: null,
		year: null,
		sixMonths: true,
		allTime: null
	})

	const categoriesColorMap = categories.reduce(
		(acc, { title }, i) => ({ ...acc, [title]: categoriesColors[i % categoriesColors.length] }),
		{}
	)

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
					<ChartDescription id={'homepage-treemap-chart-label'}>
						Showing incidents grouped by type of attack. An incident can fall under more than one
						category.
					</ChartDescription>
					<TreeMap
						data={datasetFiltered}
						width={chartWidth}
						height={chartHeight}
						id={'homepage-treemap-chart-label'}
						isHomePageDesktopView={width > 970}
						minimumBarHeight={35}
						categoryColumn={'categories'}
						titleLabel={'incidents'}
						openSearchPage={(category) => {
							goToFilterPage(databasePath, { category }, currentDate, categories)
						}}
						categoriesColors={categoriesColorMap}
						allCategories={Object.keys(categoriesColorMap)}
					/>
				</div>
				<div className={'hpChart'}>
					<ChartDescription id={'homepage-usmap-chart-label'}>
						Showing incidents distribution in the U.S. Incidents are grouped by state.
					</ChartDescription>
					<USMap
						data={datasetAggregatedByGeo}
						incidentsOutsideUS={incidentsOutsideUS}
						width={chartWidth}
						height={chartHeight}
						id={'homepage-usmap-chart-label'}
						openSearchPage={(state) => {
							goToFilterPage(databasePath, { ...filtersApplied, state }, currentDate, categories)
						}}
					/>
				</div>
				<div className={'hpChart'}>
					<ChartDescription id={'homepage-bar-chart-label'}>Showing the number of journalists targeted per month.</ChartDescription>
					<BarChart
						data={datasetGroupedByMonth}
						x={'monthName'}
						y={'numberOfIncidents'}
						titleLabel={'incidents'}
						id={'homepage-bar-chart-label'}
						width={chartWidth}
						height={chartHeight}
						isMobileView={width < 970}
						openSearchPage={(monthName) => {
							goToFilterPage(databasePath, { ...filtersApplied, monthName }, currentDate, categories)
						}}
					/>
				</div>
			</div>
		</Flashing>
	)
}
