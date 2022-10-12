import React, { useRef } from 'react'
import { ParentSize } from '@visx/responsive'
import Flashing from '../../../common/js/components/Flashing'
import BarChartYears from "./BarChartYears"
import {
	filterDatasetByFiltersApplied,
	groupByMonthSorted,
	monthIndexes,
	groupByState,
	countIncidentsOutsideUS,
	categoriesColors,
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
	currentDate = new Date(),
	loading = false,
}) {
	const chartWidth = width > 970 ? width / 3 : width
	const chartHeight = width > 970 ? 500 : 480

	const datasetGroupedByYears = groupByYearsSorted(dataset)

	return (
		<Flashing flashing={loading}>
			<div className={'cpChartContainer'} style={{ width: width }}>
				<div className={'cpChart'}>
					<ChartDescription>Showing the number of incidents per year.</ChartDescription>
					{/* <BarChartYears
						width={chartWidth}
						height={chartHeight}
						countYears={countYears}
						selectedYears={selectedYears}
						setSelectedYears={setSelectedYears}
						onClick={onYearClick}
					/> */}
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
