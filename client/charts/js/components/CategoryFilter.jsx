import React from 'react'
import * as d3 from 'd3'
import { countBy } from 'lodash'
import { AnimatedDataset } from 'react-animated-dataset'
import CategorySection from './CategorySection'
import FilterSet from './FilterSet'

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

function RadioFilter({
	name,
	label,
	choices,
	value,
}) {
	let id = `id_${name}`
	return (
		<div className="filters__field-row">
			<div className="filters__field-label">
				{label}
			</div>
			<ul id={id}>

				<li>
					<label for={`id_${name}_0`}>
						<input type="radio" name={name} value="1" id={`id_${name}_0`}/>Yes
					</label>
				</li>
				<li><label for={`id_${name}_1`}><input checked={value} type="radio" name={name} value="0" id={`id_${name}_1`}/>No</label></li>
			</ul>
		</div>
	)
}

export default function CategoryFilter({
	dataset,
	width,
	height,
	filterDefs,
	filterParameters,
	setFilterParameters,
}) {
	const selectedCategories = filterParameters.filterCategory.parameters

	let categoryFrequencies = {}
	filterDefs.forEach(c => categoryFrequencies[c.title] = 0)
	const incidents = dataset.flatMap(({ categories, ...d }) =>
		categories.map((category) => ({ ...d, category }))
	)
	categoryFrequencies = {
		...categoryFrequencies,
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

	function selectCategoryIfHasCount(categoryName) {
		let count = categoryFrequencies[categoryName]
		if (count === 0) {
			return null
		} else {
			return onCategoryClick(categoryName)
		}
	}

	function onCategoryClick(d) {
		let targetCategory
		if (typeof d == 'string') {
			targetCategory = d
		} else if (d.hasOwnProperty('category')) {
			targetCategory = d.category
		} else {
			console.log("else")
		}
		const newCategories = (oldCategories) =>
			oldCategories.includes(targetCategory)
				? oldCategories.filter((cat) => cat !== targetCategory)
				: [...oldCategories, targetCategory]
		setFilterParameters('filterCategory', newCategories)
	}

	function handleFilterChange(event) {
		setFilterParameters(event.target.name, event.target.value)
	}

	return (
		<div className="filters__form--fieldset">
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
						onClick: (d, i) => {
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
								transform={'translate(0, -7)'}
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
			{filterDefs.map(filterDef =>
				<CategorySection
					key={filterDef.id}
					label={filterDef.title}
					count={categoryFrequencies[filterDef.title]}
					isOpen={selectedCategories.includes(filterDef.title)}
					onClick={selectCategoryIfHasCount}
				>
					<FilterSet
						filters={filterDef.filters}
						filterParameters={filterParameters}
						handleFilterChange={handleFilterChange}
						setFilterParameters={setFilterParameters}
					/>
				</CategorySection>
			)}
		</div>
	)
}
