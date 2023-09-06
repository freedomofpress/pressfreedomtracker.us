import React, { useContext } from 'react'
import classNames from 'classnames'
import * as d3 from 'd3'
import { countBy } from 'lodash'
import { AnimatedDataset } from 'react-animated-dataset'
import CategorySection from './CategorySection'
import FilterSet from './FilterSet'
import { FiltersDispatch } from '../lib/context'
import {
	TOGGLE_PARAMETER_ITEM,
	SET_PARAMETER,
} from '../lib/actionTypes'
import { trackMatomoEvent } from '../lib/utilities'

const margins = {
	top: 15,
	left: 5,
	right: 30,
	bottom: 30,
}

export default function CategoryFilter({
	dataset,
	width,
	height,
	filterDefs,
	filterParameters,
	filterWithout,
}) {
	const selectedCategories = filterParameters.categories?.parameters || []
	const updateFilters = useContext(FiltersDispatch);

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
				symbol: filterDefs.find(d => d.title === curr)?.symbol
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
		updateFilters({type: TOGGLE_PARAMETER_ITEM, payload: { item: targetCategory, filterName: 'categories'}})
		// Fire matomo event
		trackMatomoEvent(['Filter', 'Categories', 'Change', targetCategory])
	}

	function handleFilterChange(event) {
		updateFilters({
			type: SET_PARAMETER,
			payload: {
				filterName: event.target.name,
				value: event.target.value,
			},
		})

		// Fire matomo event
		trackMatomoEvent(['Filter', 'Categories', 'Filter', event.target.name, event.target.value])
	}

	return (
		<div className="filters__form--fieldset">
			<div className="category-graph">
				<p className="category-graph--label" id="categories-graph-label">Filter by one or more categories</p>
				<svg
					width={width}
					height={height}
					key={'BarChartCategories'}
					style={{ fontFamily: 'var(--font-mono)' }}
					className="category-graph--figure"
					aria-labelledby="categories-graph-label"
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
							fill: (d) => (selectedCategories.has && selectedCategories.has(d.category) ? '#F2FC67' : 'black'),
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
								<foreignObject
									width={imageWidth}
									height={imageWidth}
									x={xScale(d.category) + barsWidth / 2 - imageWidth / 2}
									y={height - margins.bottom / 2}
									transform={'translate(0, -7)'}
									opacity={d.count === 0 ? 0.3 : 1}
								>
									<div
										className={classNames('category', `category-${d.symbol}`)}
										onClick={() => {
											if (d.count === 0) {
												return null
											} else {
												return onCategoryClick(d)
											}
										}}
									/>
								</foreignObject>
							</g>
						)
					})}
				</svg>
			</div>
			{filterDefs.map(filterDef =>
				<CategorySection
					key={filterDef.id}
					symbol={filterDef.symbol}
					label={filterDef.title}
					count={categoryFrequencies[filterDef.title]}
					isOpen={!!selectedCategories.has && selectedCategories.has(filterDef.title)}
					onClick={selectCategoryIfHasCount}
				>
					<FilterSet
						filters={filterDef.filters}
						filterParameters={filterParameters}
						handleFilterChange={handleFilterChange}
						width={width}
						filterWithout={filterWithout}
					/>
				</CategorySection>
			)}
		</div>
	)
}
