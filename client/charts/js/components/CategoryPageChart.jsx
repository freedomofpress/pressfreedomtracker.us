import React, { useRef } from 'react'
import { ParentSize } from '@visx/responsive'
import Flashing from '../../../common/js/components/Flashing'
import ChartDescription from "./ChartDescription"
import BarChartHomepage from "./BarChartHomepage"
import {
	goToFilterPage,
	groupByYearsSorted,
} from '../lib/utilities.js'

import '../../sass/HomepageMainCharts.sass'

export default function CategoryPageChart(props) {
	return (
		<ParentSize>
			{(parent) => <CategoryPageChartWidth {...props} width={parent.width} />}
		</ParentSize>
	)
}

function CategoryPageChartWidth({
	data: dataset,
	width,
	category,
	databasePath = window.location.pathname,
	loading = false,
}) {
	const chartWidth = width > 970 ? width / 3 : width
	const chartHeight = width > 970 ? 500 : 480

	const datasetGroupedByYears = groupByYearsSorted(dataset)

	return (
		<Flashing flashing={loading}>
			<div className={'cpChartContainer'} style={{ width: width }}>
				<div className={'cpChart'}>
					<ChartDescription id={'category-page-chart-label'}>Showing the number of incidents per year.</ChartDescription>
					<BarChartHomepage
						data={datasetGroupedByYears}
						x={'year'}
						y={'numberOfIncidents'}
						titleLabel={'incidents'}
						id={'category-page-chart-label'}
						width={chartWidth}
						height={chartHeight}
						isMobileView={width < 970}
						openSearchPage={(year) => {
							goToFilterPage(databasePath, {category, year}, new Date())
						}}
					/>
				</div>
			</div>
		</Flashing>
	)
}
