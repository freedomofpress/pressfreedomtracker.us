import React from 'react'
import * as d3 from 'd3'
import { sortBy, countBy } from 'lodash'
import { AnimatedDataset } from 'react-animated-dataset'
import { firstDayOfMonth } from '../lib/utilities'

const margins = {
	top: 15,
	left: 5,
	right: 30,
	bottom: 3,
}

function isDateValid(date) {
	return !Number.isNaN(new Date(date).getYear())
}

function monthWidth(date, scale) {
	return scale(d3.timeMonth.offset(new Date(date), 1)) - scale(new Date(date))
}

export default function TimeMonthsFilter({
	width,
	height,
	dateExtents,
	dataset,
	filterParameters: selectedDateRange,
	setFilterParameters: setSelectedDateRange,
}) {
	const [minDate, maxDate] = dateExtents

	function closeLineArea(dataset) {
		return [
			{
				date: minDate,
				count: 0,
			},
			...dataset,
			{
				date: maxDate,
				count: 0,
			},
		]
	}

	const monthFrequenciesObj = {
		...Object.fromEntries(
			d3.timeMonth.range(minDate, maxDate).map((date) => [date.toISOString(), 0])
		),
		...countBy(dataset, (d) => firstDayOfMonth(d.date).toISOString()),
	}
	const monthFrequencies = sortBy(
		Object.entries(monthFrequenciesObj).map(([dateISO, count]) => ({
			date: dateISO,
			count,
		})),
		'date'
	)

	const datasetSelected = dataset.filter(
		(d) =>
			new Date(d.date).getTime() >= selectedDateRange.min.getTime() &&
			new Date(d.date).getTime() <= selectedDateRange.max.getTime()
	)

	const monthFrequenciesSelectedObj = {
		...Object.fromEntries(
			d3.timeMonth.range(minDate, maxDate).map((date) => [date.toISOString(), 0])
		),
		...countBy(datasetSelected, (d) => firstDayOfMonth(d.date).toISOString()),
	}
	const monthFrequenciesSelected = sortBy(
		Object.entries(monthFrequenciesSelectedObj).map(([dateISO, count]) => ({
			date: dateISO,
			count,
		})),
		'date'
	)

	const xScale = d3
		.scaleTime()
		.domain(dateExtents)
		.range([1 + margins.left, width - margins.right])

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(monthFrequencies.map((d) => d.count))])
		.range([0 + margins.top, height - margins.bottom - margins.top])
		.nice(3)

	const yScaleLine = yScale.copy().range([height - margins.bottom - margins.top, 0 + margins.top])

	const lineGenerator = d3
		.line()
		.curve(d3.curveStepAfter)
		.x((d) => xScale(new Date(d.date)))
		.y((d) => yScaleLine(d.count))

	return (
		<div style={{ flexDirection: 'row' }}>
			<svg width={width} height={height} style={{ fontFamily: 'var(--font-mono)' }}>
				<AnimatedDataset
					dataset={yScale.ticks(3)}
					tag="line"
					init={{
						opacity: 0,
					}}
					attrs={{
						x1: margins.left,
						x2: width,
						y1: (tick, i) => height - margins.bottom - yScale(tick, i) + (i === 0 ? 1.5 : 0),
						y2: (tick, i) => height - margins.bottom - yScale(tick) + (i === 0 ? 1.5 : 0),
						stroke: 'black',
						strokeWidth: (_, i) => (i === 0 ? 3 : 1),
						opacity: 1,
					}}
					keyFn={(d) => d}
					duration={450}
				/>
				<AnimatedDataset
					dataset={yScale.ticks(3)}
					tag="text"
					init={{
						opacity: 0,
					}}
					attrs={{
						x: width,
						y: (tick) => height - margins.bottom - yScale(tick) - 4,
						text: (tick) => tick,
						textAnchor: 'end',
						fontSize: 12,
						opacity: 1,
					}}
					keyFn={(d) => d}
					duration={450}
				/>
				<AnimatedDataset
					dataset={monthFrequencies}
					tag="rect"
					attrs={{
						x: (d) => xScale(new Date(d.date)),
						y: (d) => height - margins.bottom - yScale(d.count),
						fill: 'black',
						width: (d) => monthWidth(d.date, xScale) + 0.5,
						height: (d) => yScale(d.count) - margins.top,
						key: (_, i) => i,
					}}
					duration={300}
					keyFn={(d) => d.date}
				/>
				<AnimatedDataset
					dataset={monthFrequenciesSelected}
					tag="rect"
					attrs={{
						x: (d) => xScale(new Date(d.date)),
						y: (d) => height - margins.bottom - yScale(d.count),
						fill: '#F2FC67',
						width: (d) => monthWidth(d.date, xScale) + 0.5,
						height: (d) => yScale(d.count) - margins.top,
						key: (_, i) => i,
					}}
					duration={300}
					keyFn={(d) => d.date}
				/>
				<AnimatedDataset
					dataset={[monthFrequencies]}
					tag="path"
					attrs={{
						d: (d) => lineGenerator(sortBy(closeLineArea(monthFrequenciesSelected), (d) => d.date)),
						stroke: 'black',
						strokeWidth: 1,
						fill: 'none',
					}}
					duration={300}
					keyFn={(d, i) => i}
				/>
			</svg>

			<div
				style={{
					display: 'flex',
					width: '100%',
					justifyContent: 'space-between',
				}}
			>
				<input
					type={'date'}
					value={selectedDateRange.min.toISOString().slice(0, 10)}
					min={dateExtents[0].toISOString().slice(0, 10)}
					max={dateExtents[1].toISOString().slice(0, 10)}
					onChange={(event) => {
						if (isDateValid(event.target.value)) {
							const newDateRange = (oldDateRange) => {
								return { ...oldDateRange, min: new Date(event.target.value) }
							}
							setSelectedDateRange('filterTimeMonths', newDateRange)
						}
					}}
					style={{ flexBasis: '50%' }}
				/>
				<input
					type={'date'}
					value={selectedDateRange.max.toISOString().slice(0, 10)}
					min={dateExtents[0].toISOString().slice(0, 10)}
					max={dateExtents[1].toISOString().slice(0, 10)}
					onChange={(event) => {
						if (isDateValid(event.target.value)) {
							const newDateRange = (oldDateRange) => {
								return { ...oldDateRange, max: new Date(event.target.value) }
							}
							setSelectedDateRange('filterTimeMonths', newDateRange)
						}
					}}
					style={{ flexBasis: '50%' }}
				/>
			</div>
		</div>
	)
}
