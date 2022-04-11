import React, { useState } from 'react'
import * as d3 from 'd3'
import { AnimatedDataset } from 'react-animated-dataset'
import Tooltip from './Tooltip'
import { colors } from '../lib/utilities.js'

// React-animated-dataset uses an older version of
// d3 selection and in order to access some of its
// functionality, we need this separate import.
// See for details:
// * https://github.com/accurat/react-animated-dataset/issues/24
// * https://github.com/d3/d3-selection/tree/v1.4.1#event
//
// This can be removed when RAD is updated to use a newer version
import { event as d3event } from 'd3-selection'

const margins = {
	top: 0,
	left: 0,
	right: 0,
	bottom: 0,
}

const paddings = {
	top: 0,
	bottom: 40.5,
	right: 10,
	left: 10,
}

const textPaddings = {
	left: 10,
	right: 10,
	top: 5,
}

const borderWidth = {
	hover: 7,
	normal: 5,
}

const textStyle = {
	fontFamily: 'var(--font-base)',
	fontWeight: '500',
	fontSize: '14px',
	lineHeight: '17px',
}

const paddingRect = borderWidth.normal
const minimumHeightText = 17

function computeMinimumNumberOfIncidents(dataset, chartHeight, minimumBarHeight) {
	const totalIncidents = dataset.length

	const y = d3
		.scaleLinear()
		.domain([0, totalIncidents])
		.range([0, chartHeight - borderWidth.normal - paddings.top - paddings.bottom])

	// totalIncidents + 1 is needed in case there's only one incident (otherwise d3.range(1) => [0])
	const minimumNumberOfIncidents = d3.min(
		d3.range(totalIncidents + 1).filter((d) => y(d) > minimumBarHeight)
	)

	return minimumNumberOfIncidents
}

function stackDatasetByCategory(
	dataset,
	categoryColumn,
	categoryDivider,
	minimumNumberOfIncidents,
	allCategories
) {
	const categories = dataset.map((d) => d[categoryColumn]).filter((d) => d != null)

	// Any incident having multiple categories is counted once per category
	const categoriesSimplified = [].concat.apply(
		[],
		categories.map((d) => d.split(categoryDivider).map((e) => e.trim()))
	)

	// {"Assault": 800, "Arrest": 50, ...}
	const incidentsGroupedByCategory =
		allCategories !== undefined
			? Object.fromEntries(
					allCategories.map((d) => [d, categoriesSimplified.filter((e) => e === d).length])
				)
			: Object.fromEntries(
					d3.rollup(
						categoriesSimplified.map((d) => ({ category: d })),
						(v) => v.length,
						(d) => d.category
					)
				)

	const incidentsGroupedByCategoryAdjusted = Object.fromEntries(
		d3.rollup(
			categoriesSimplified.map((d) => ({ category: d })),
			(v) => (v.length === 0 ? 0 : Math.max(v.length, minimumNumberOfIncidents)),
			(d) => d.category
		)
	)

	// [{category: "Assault", startingPoint: 0, endPoint: 800}, {category: "Arrest", startingPoint: 800, endPoint: 850}, ...]
	const stack = d3.stack().keys(Object.keys(incidentsGroupedByCategory))
	const datasetStackedByCategory = stack([incidentsGroupedByCategoryAdjusted]).map((d) => ({
		startingPoint: d[0][0],
		endPoint: !isNaN(d[0][1]) ? d[0][1] : d[0][0],
		numberOfIncidents: incidentsGroupedByCategory[d.key],
		category: d.key,
	}))

	return datasetStackedByCategory
}

export default function TreeMap({
	data: dataset,
	categoryColumn,
	categoryDivider = ',',
	width,
	height,
	isHomePageDesktopView,
	minimumBarHeight,
	openSearchPage,
	categoriesColors,
	allCategories,
}) {
	const [hoveredElement, setHoveredElement] = useState(null)
	const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })

	const updateTooltipPosition = (MouseEvent) => {
		setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
	}

	const minimumNumberOfIncidents = computeMinimumNumberOfIncidents(
		dataset,
		height,
		minimumBarHeight
	)

	const datasetStackedByCategory = stackDatasetByCategory(
		dataset,
		categoryColumn,
		categoryDivider,
		minimumNumberOfIncidents,
		allCategories
	)

	const yScale = d3
		.scaleLinear()
		// Default to [-1, 0] if there's no data
		.domain(dataset.length ? [0, d3.max(datasetStackedByCategory, (d) => d.endPoint)] : [-1, 0])
		.range([height - borderWidth.normal - paddings.top, paddings.bottom])

	const computeBarHeight = (start, end) => {
		return Math.max(yScale(start) - yScale(end), 1)
	}

	const getCategoryColour = (category) => {
		return categoriesColors[category]
	}

	const colorScale = categoriesColors !== undefined ? getCategoryColour : d3.scaleOrdinal(colors)

	const colorsByCategory = datasetStackedByCategory
		.filter((d) => d.numberOfIncidents !== 0)
		.map((d) => ({
			category: d.category,
			color: colorScale(d.category),
		}))

	const findColor = (cat) => colorsByCategory.find((d) => d.category === cat).color

	function nextCategory(dataset, i) {
		const nextCategories = dataset.slice(i + 1).filter((d) => d.numberOfIncidents !== 0)
		return nextCategories.length === 0 ? null : nextCategories[0].category
	}

	if (!width) return null

	return (
		<>
			{hoveredElement && (
				<Tooltip
					content={
						<div style={{ fontFamily: 'var(--font-base)', fontSize: 12, fontWeight: 500 }}>
							<div>Number of Incidents</div>
							<div
								style={{ display: 'flex', justifyContent: 'space-between', gap: 15, marginTop: 8 }}
							>
								<div
									style={{ borderLeft: `solid 3px ${findColor(hoveredElement)}`, paddingLeft: 3 }}
								>
									{hoveredElement}
								</div>
								<div>
									{
										datasetStackedByCategory.find((d) => d.category === hoveredElement)
											.numberOfIncidents
									}
								</div>
							</div>
						</div>
					}
					x={tooltipPosition.x}
					y={tooltipPosition.y}
				/>
			)}
			<div>
				<svg
					width={width}
					height={height}
					style={{
						marginTop: margins.top,
						marginRight: margins.right,
						marginBottom: margins.bottom,
						marginLeft: margins.left,
					}}
				>
					<line
						x1={paddings.left}
						x2={width}
						y1={height - paddings.bottom + 0.5}
						y2={height - paddings.bottom + 0.5}
						style={{ stroke: 'black', strokeWidth: isHomePageDesktopView ? borderWidth.normal : 0 }}
						shapeRendering="crispEdges"
					/>
					<AnimatedDataset
						dataset={datasetStackedByCategory}
						tag="rect"
						init={{
							opacity: 0,
							x: paddings.left,
							y: height - paddings.bottom,
							width: width - (paddings.right + paddings.left),
							height: 0,
						}}
						attrs={{
							opacity: 1,
							x: paddings.left,
							y: (d) => height - yScale(d.startingPoint),
							width: width - (paddings.right + paddings.left),
							height: (d) => computeBarHeight(d.startingPoint, d.endPoint),
							fill: (d) =>
								hoveredElement === d.category || hoveredElement === null
									? d.numberOfIncidents === 0
										? 'white'
										: findColor(d.category)
									: 'white',
							stroke: (d) => (hoveredElement === d.category ? findColor(d.category) : 'black'),
							strokeWidth: borderWidth.normal,
							cursor: 'pointer',
							pointerEvents: (d) => (d.numberOfIncidents === 0 ? 'none' : null),
							shapeRendering: 'crispEdges',
						}}
						events={{
							// In a future, if we update our version of d3-selection the first
							// argument will be a MouseEvent, eliminating the need for d3event here
							onMouseMove: () => {
								updateTooltipPosition(d3event)
							},
							onMouseLeave: () => {
								setHoveredElement(null)
							},
							// In a future, if we update our version of d3-selection this may
							// need to be updated to take arguments (MouseEvent, d) instead
							onMouseEnter: d => setHoveredElement(d.category),
							onMouseUp: d => openSearchPage(d.category),
						}}
						durationByAttr={{ fill: 0, stroke: 0 }}
						keyFn={(d) => d.category}
						duration={250}
					/>
					<AnimatedDataset
						dataset={datasetStackedByCategory}
						tag="line"
						init={{
							opacity: 0,
							x1: paddings.left - borderWidth.normal / 2,
							x2: width - paddings.right + borderWidth.normal / 2,
							y1: height - paddings.bottom,
							y2: height - paddings.bottom,
						}}
						attrs={{
							opacity: (d) =>
								datasetStackedByCategory
									.filter((d) => d.startingPoint !== d.endPoint)
									.map((d) => d.category)
									.includes(d.category)
									? 1
									: 0,
							display: (d) => (d.startingPoint !== d.endPoint ? null : 'none'),
							x1: paddings.left - borderWidth.normal / 2,
							x2: width - paddings.right + borderWidth.normal / 2,
							y1: (d) =>
								height - yScale(d.startingPoint) + computeBarHeight(d.startingPoint, d.endPoint),
							y2: (d) =>
								height - yScale(d.startingPoint) + computeBarHeight(d.startingPoint, d.endPoint),
							stroke: (d, i) =>
								hoveredElement === d.category
									? findColor(d.category)
									: hoveredElement !== null &&
										hoveredElement === nextCategory(datasetStackedByCategory, i)
									? findColor(nextCategory(datasetStackedByCategory, i))
									: 'black',
							strokeWidth: borderWidth.normal + 1,
							pointerEvents: 'none',
							shapeRendering: 'crispEdges',
						}}
						keyFn={(d) => d.category}
						duration={250}
						durationByAttr={{ fill: 0, stroke: 0 }}
					/>
					<AnimatedDataset
						dataset={datasetStackedByCategory}
						tag="text"
						init={{
							opacity: 0,
							y: (d) => height - paddings.bottom,
							x: paddings.left + textPaddings.left,
						}}
						attrs={{
							opacity: (d) =>
								datasetStackedByCategory
									.filter(
										(d) =>
											yScale(d.startingPoint) - yScale(d.endPoint) - paddingRect > minimumHeightText
									)
									.map((d) => d.category)
									.includes(d.category)
									? 1
									: 0,
							y: (d) =>
								height -
								yScale(d.startingPoint) +
								computeBarHeight(d.startingPoint, d.endPoint) / 2 +
								textPaddings.top,
							x: paddings.left + textPaddings.left,
							textAnchor: 'start',
							...textStyle,
							pointerEvents: 'none',
							text: (d) => d.category,
						}}
						keyFn={(d) => d.category}
						duration={250}
					/>
					<AnimatedDataset
						dataset={datasetStackedByCategory}
						init={{
							opacity: 0,
							y: (d) => height - paddings.bottom,
							x: width - textPaddings.right - paddings.right,
						}}
						tag="text"
						attrs={{
							opacity: (d) =>
								datasetStackedByCategory
									.filter(
										(d) =>
											yScale(d.startingPoint) - yScale(d.endPoint) - paddingRect > minimumHeightText
									)
									.map((d) => d.category)
									.includes(d.category)
									? 1
									: 0,
							y: (d) =>
								height -
								yScale(d.startingPoint) +
								computeBarHeight(d.startingPoint, d.endPoint) / 2 +
								textPaddings.top,
							x: width - textPaddings.right - paddings.right,
							textAnchor: 'end',
							...textStyle,
							pointerEvents: 'none',
							text: (d) => d.numberOfIncidents,
						}}
						keyFn={(d) => d.category}
						duration={250}
					/>
				</svg>
			</div>
		</>
	)
}
