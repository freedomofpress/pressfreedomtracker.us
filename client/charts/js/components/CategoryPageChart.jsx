import React, { useRef } from 'react'
import { ParentSize } from '@visx/responsive'
import Flashing from '../../../common/js/components/Flashing'
import ChartDescription from "./ChartDescription"
import BarChart from "./BarChart"
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
	categoryName,
	vizType,
	databasePath = window.location.pathname,
	loading = false,
}) {
	const chartHeight = width > 480 ? 500 : 480

	const datasetGroupedByYears = groupByYearsSorted(dataset)

	return (
		<Flashing flashing={loading}>
			<div className={'cpChartContainer'} style={{ width: width }}>
				<div className={'cpChart'}>
					<ChartDescription id={'category-page-chart-label'}>
						Number of {categoryName} incidents per year.
					</ChartDescription>
					{ vizType === 'bar' && (
						<BarChart
							data={datasetGroupedByYears}
							x={'year'}
							y={'numberOfIncidents'}
							titleLabel={'incidents'}
							id={'category-page-chart-label'}
							width={width}
							height={chartHeight}
							isMobileView={width < 480}
							openSearchPage={(year) => {
								goToFilterPage(databasePath, {category, year}, new Date())
							}}
						/>
					)}
				</div>
			</div>
		</Flashing>
	)
}
