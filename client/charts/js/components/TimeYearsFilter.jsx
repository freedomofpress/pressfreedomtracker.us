import React from 'react'
import { countBy, range } from 'lodash'
import BarChartYears from './BarChartYears'
import CheckBoxesYear from './CheckBoxesYear'

export default function TimeYearsFilter({
	width,
	height,
	dateExtents,
	dataset,
	filterParameters: selectedYears,
	setFilterParameters: setSelectedYears,
}) {
	const [minDateYear, maxDateYear] = dateExtents.map((date) => date.getFullYear())
	const allYears = range(minDateYear, maxDateYear)

	const initializeYears = Object.fromEntries(allYears.map((year) => [year, 0]))

	const countedYears = countBy(dataset, (d) => {
		return new Date(d.date).getFullYear()
	})

	const years = { ...initializeYears, ...countedYears }

	const countYears = Object.entries(years).map(([year, count]) => ({
		year: Number(year),
		count,
	}))

	function onYearClick(d) {
		const newYears = (oldYears) =>
			oldYears.includes(d.year) ? oldYears.filter((year) => year !== d.year) : [...oldYears, d.year]
		setSelectedYears('filterTimeYears', newYears)
	}

	return (
		<div style={{ flexDirection: 'row' }}>
			<BarChartYears
				width={width}
				height={height}
				countYears={countYears}
				selectedYears={selectedYears}
				setSelectedYears={setSelectedYears}
				onClick={onYearClick}
			/>

			<CheckBoxesYear
				width={width}
				options={countYears}
				selectedYears={selectedYears}
				setSelectedYears={setSelectedYears}
				onClick={onYearClick}
			/>
		</div>
	)
}
