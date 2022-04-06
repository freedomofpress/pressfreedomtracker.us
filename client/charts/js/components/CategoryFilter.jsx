import React from 'react'
import * as d3 from 'd3'
import { countBy } from 'lodash'
import { AnimatedDataset } from 'react-animated-dataset'

import strokeCircle from './svgIcons/strokeCircle.svg'
import fillCircle from './svgIcons/fillCircle.svg'
import rhombus from './svgIcons/rhombus.svg'
import doubleCircle from './svgIcons/doubleCircle.svg'
import doubleCircleFill from './svgIcons/doubleCircleFill.svg'
import sixPointStar from './svgIcons/sixPointStar.svg'
import compassRose from './svgIcons/compassRose.svg'
import diamondStar from './svgIcons/diamondStar.svg'
import superSun from './svgIcons/superSun.svg'
import sunStar from './svgIcons/sunStar.svg'
import flower from './svgIcons/flower.svg'

const margins = {
	top: 15,
	left: 5,
	right: 30,
	bottom: 30,
}

const svgIcons = {
	'Assault': strokeCircle,
	'Arrest/Criminal Charge': fillCircle,
	'Arrest / Criminal Charge': fillCircle, // redundant to catch both
	'Equipment Damage': doubleCircle,
	'Equipment Search or Seizure': doubleCircleFill,
	'Chilling Statement': sixPointStar,
	'Denial of Access': compassRose,
	'Leak Case': rhombus,
	'Prior Restraint': diamondStar,
	'Subpoena/Legal Order': sunStar,
	'Subpoena / Legal Order': sunStar, // redundant to catch both
	'Other Incident': flower,
	'Border Stop': superSun,
}

export default function CategoryFilter({
	dataset,
	width,
	height,
	filterParameters: selectedCategories,
	setFilterParameters: setSelectedCategories,
}) {
	const incidents = dataset.flatMap(({ categories, ...d }) =>
		categories.map((category) => ({ ...d, category }))
	)

	const categoryFrequencies = {
		'Assault': 0,
		'Arrest/Criminal Charge': 0,
		'Equipment Damage': 0,
		'Equipment Search or Seizure': 0,
		'Chilling Statement': 0,
		'Denial of Access': 0,
		'Leak Case': 0,
		'Prior Restraint': 0,
		'Subpoena/Legal Order': 0,
		'Other Incident': 0,
		'Border Stop': 0,
		...countBy(incidents, (d) => {
			return d.category
		}),
	}

	const countCategories = Object.keys(categoryFrequencies).reduce(
		(acc, curr) => [
			...acc,
			{
				category: curr,
				count: categoryFrequencies[curr],
			},
		],
		[]
	)

	const maxCategoryCount =
		d3.max(countCategories.map((d) => d.count)) === 0
			? 1
			: d3.max(countCategories.map((d) => d.count))

	const xScale = d3
		.scaleBand()
		.domain(countCategories.map((d) => d.category).sort())
		.range([0 + margins.left, width - margins.right])

	const yScale = d3
		.scaleLinear()
		.domain([0, maxCategoryCount])
		.range([0, height - margins.bottom - margins.top])
		.nice(3)

	const barsWidth = (width - margins.right) / 20
	const imageWidth = 14

	function onCategoryClick(d) {
		const newCategories = (oldCategories) =>
			oldCategories.includes(d.category)
				? oldCategories.filter((cat) => cat !== d.category)
				: [...oldCategories, d.category]
		setSelectedCategories('filterCategory', newCategories)
	}

	return (
		<svg
			width={width}
			height={height}
			key={'BarChartCategories'}
			style={{ fontFamily: 'var(--font-mono)' }}
		>
			<AnimatedDataset
				dataset={yScale.ticks(3)}
				tag="line"
				init={{
					opacity: 0,
				}}
				attrs={{
					x1: margins.left,
					x2: width,
					y1: (tick) => height - margins.bottom - yScale(tick),
					y2: (tick) => height - margins.bottom - yScale(tick),
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
				dataset={countCategories}
				tag="rect"
				attrs={{
					x: (d) => xScale(d.category),
					y: (d) => height - margins.bottom - yScale(d.count),
					fill: (d) => (selectedCategories.includes(d.category) ? '#F2FC67' : 'black'),
					width: barsWidth,
					stroke: 'black',
					strokeWidth: 2,
					height: (d) => yScale(d.count),
					key: (_, i) => i,
				}}
				events={{
					onClick: (_, d) => {
						onCategoryClick(d)
					},
				}}
				durationByAttr={{ fill: 0 }}
				duration={250}
				keyFn={(d) => d.category}
			/>

			{countCategories.map((d, i) => {
				return (
					<g key={i}>
						<image
							width={imageWidth}
							height={imageWidth}
							x={xScale(d.category) + barsWidth / 2 - imageWidth / 2}
							y={height - margins.bottom / 2}
							href={svgIcons[d.category]}
							transform={'translate(-50% ,0)'}
							opacity={d.count === 0 ? 0.3 : 1}
							onClick={() => {
								if (d.count === 0) {
									return null
								} else {
									return onCategoryClick(d)
								}
							}}
						/>
					</g>
				)
			})}
		</svg>
	)
}
