import React, { useState } from 'react'
import * as d3 from 'd3'
import { AnimatedDataset } from 'react-animated-dataset'
import DynamicWrapper from './DynamicWrapper'
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
	top: 10,
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
	mobile: 3,
}

const textStyle = {
	fontFamily: 'var(--font-base)',
	fontWeight: '500',
	fontSize: '14px',
	lineHeight: '17px',
}

const paddingRect = borderWidth.normal
const minimumHeightText = 17
const averageLetterWidth = 8
const labelHeight = 30

export function computeMinimumNumberOfIncidents(dataset, chartHeight, minimumBarHeight) {
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

export function stackDatasetByCategory(
	dataset,
	filterElements,
	categoryColumn,
	categoryDivider,
	minimumNumberOfIncidents,
	allCategories
) {
	const categories = dataset.map((d) => d[categoryColumn]).filter((d) => d != null)

	// Any incident having multiple categories is counted once per category
	const categoriesSimplified = [].concat.apply(
		[],
		categories.map(
			(d) => d.split(categoryDivider).map((e) => e.trim())
				.filter(f => !filterElements || filterElements.length === 0 || filterElements.includes(f))
		)
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
	const stack = d3.stack().keys(
		Object.keys(incidentsGroupedByCategory).sort((a, b) => a.localeCompare(b))
	)
	const datasetStackedByCategory = stack([incidentsGroupedByCategoryAdjusted]).map((d) => ({
		startingPoint: d[0][0],
		endPoint: !isNaN(d[0][1]) ? d[0][1] : d[0][0],
		numberOfIncidents: incidentsGroupedByCategory[d.key],
		category: d.key,
	})).filter((d) => d.numberOfIncidents > 0)  // Only display non-empty groups in the chart.

	return datasetStackedByCategory
}

export default function TreeMap({
	data: dataset,
	categoryColumn,
	id = '',
	categoryDivider = ',',
	width,
	height,
	isHomePageDesktopView,
	minimumBarHeight,
	searchPageURL,
	categoriesColors,
	allCategories,
	// function prop received from ChartDownloader that binds the svg element to allow
	// it to be downloaded
	setSvgEl = () => {},
	interactive = true,
}) {
	const [hoveredElement, setHoveredElement] = useState(null)
	const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })
	const [selectedElements, setSelectedElements] = useState([])

	// Because the chart can be rendered horizontally on desktop and vertically on
	// mobile, we abstract the dimensions below
	const isMobile = width < 500
	const chartLength = isMobile ? height : width
	const chartWidth = isMobile ? width : height
	const chartLengthPaddingBefore = isMobile ? paddings.top : paddings.left
	const chartLengthPaddingAfter = isMobile ? paddings.bottom : paddings.right
	let chartWidthPaddingBefore = isMobile ? paddings.left : paddings.top
	const chartWidthPaddingAfter = isMobile ? paddings.right : paddings.bottom
	const chartLengthDimension = isMobile ? 'y' : 'x'
	const chartWidthDimension = isMobile ? 'x' : 'y'
	const chartLengthTitle = isMobile ? 'height' : 'width'
	const chartWidthTitle = isMobile ? 'width' : 'height'

	const updateTooltipPosition = (MouseEvent) => {
		setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
	}

	const minimumNumberOfIncidents = computeMinimumNumberOfIncidents(
		dataset,
		chartLength,
		minimumBarHeight
	)

	const datasetStackedByCategory = stackDatasetByCategory(
		dataset,
		selectedElements,
		categoryColumn,
		categoryDivider,
		minimumNumberOfIncidents,
		allCategories
	)

	const lengthScale = d3
		.scaleLinear()
		// Default to [-1, 0] if there's no data
		.domain(dataset.length ? [0, d3.max(datasetStackedByCategory, (d) => d.endPoint)] : [-1, 0])
		.range([chartLength - chartLengthPaddingBefore, chartLengthPaddingAfter])

	const computeBarHeight = (start, end) => {
		return Math.max(lengthScale(start) - lengthScale(end), 1)
	}

	const getCategoryColour = (category) => {
		return categoriesColors[category]
	}

	const colorScale = categoriesColors !== undefined ? getCategoryColour : d3.scaleOrdinal(colors)

	const colorsByCategory = datasetStackedByCategory
		.map((d) => ({
			category: d.category,
			color: colorScale(d.category),
		}))

	const findColor = (cat) => colorsByCategory.find((d) => d.category === cat)?.color || "#EEEEEE"

	function nextCategory(dataset, i) {
		const nextCategories = dataset.slice(i + 1).filter((d) => d.numberOfIncidents !== 0)
		return nextCategories.length === 0 ? null : nextCategories[0].category
	}

	// Calculate the positions of the rects for the legend
	const datasetCategoriesLabelsLegend = datasetStackedByCategory.reduce((acc, val) => {
		let labelStartingX = paddings.left
		let labelStartingY = 15
		const labelWidth = val.category.length * averageLetterWidth + 15
		if (acc.length > 0) {
			const lastLabel = acc[acc.length - 1]
			labelStartingX = lastLabel.labelStartingX + lastLabel.labelWidth
			labelStartingY = lastLabel.labelStartingY
			if (labelStartingX + labelWidth > width - paddings.right) {
				labelStartingX = paddings.left
				labelStartingY += labelHeight
			}
		}
		return [...acc, { ...val, labelStartingX, labelStartingY, labelWidth }]
	}, [])

	const toggleSelectedCategory = category => {
		const existingCategoryIndex = selectedElements.indexOf(category)
		if (existingCategoryIndex >= 0) {
			setSelectedElements(selectedElements.filter(d => d !== category))
		} else {
			setSelectedElements([...selectedElements, category])
		}
	}

	if (!isMobile) {
		chartWidthPaddingBefore = datasetCategoriesLabelsLegend[datasetCategoriesLabelsLegend.length - 1]?.labelStartingY
			+ paddings.top + labelHeight * 1.5
	}

	if (!width) return null

	return (
		<>
			{hoveredElement && interactive && !!(tooltipPosition.x || tooltipPosition.y) && (
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
					width="100%"
					aria-labelledby={id}
					style={{
						marginTop: margins.top,
						marginRight: margins.right,
						marginBottom: margins.bottom,
						marginLeft: margins.left,
						pointerEvents: interactive ? "auto" : "none",
						display: "block",
					}}
					viewBox={[0, 0, width, height]}
					ref={setSvgEl}
				>
					<line
						x1={paddings.left}
						x2={width}
						y1={height - paddings.bottom + 0.5}
						y2={height - paddings.bottom + 0.5}
						style={{ stroke: 'black', strokeWidth: isHomePageDesktopView ? borderWidth.normal : 0 }}
						shapeRendering="crispEdges"
					/>
					<DynamicWrapper
						wrapperComponent={
							<AnimatedDataset
								dataset={datasetStackedByCategory}
								tag="a"
								attrs={{
									href: d => d && searchPageURL && searchPageURL(d.category),
									role: "link",
									ariaLabel: d => d.category,
								}}
								keyFn={(d) => d.category}
							/>
						}
						wrap={interactive && searchPageURL}
					>
						<AnimatedDataset
							dataset={(interactive && searchPageURL) ? undefined : datasetStackedByCategory}
							tag="rect"
							init={{
								opacity: 0,
								[chartWidthDimension]: chartWidthPaddingBefore,
								[chartLengthDimension]: isMobile ? chartLength - chartLengthPaddingAfter : 0,
								[chartWidthTitle]: chartWidth - (chartWidthPaddingBefore + chartWidthPaddingAfter),
								[chartLengthTitle]: 0,
							}}
							attrs={{
								opacity: 1,
								[chartWidthDimension]: chartWidthPaddingBefore,
								[chartLengthDimension]: (d) => chartLength - lengthScale(d.startingPoint),
								[chartWidthTitle]: chartWidth - (chartWidthPaddingBefore + chartWidthPaddingAfter),
								[chartLengthTitle]: (d) => computeBarHeight(d.startingPoint, d.endPoint),
								fill: (d) =>
									hoveredElement === d.category || hoveredElement === null
										? d.numberOfIncidents === 0
											? 'white'
											: findColor(d.category)
										: 'white',
								stroke: (d) => (hoveredElement === d.category ? findColor(d.category) : 'black'),
								strokeWidth: isHomePageDesktopView ? borderWidth.normal : borderWidth.mobile,
								cursor: (interactive && searchPageURL) ? 'pointer' : 'inherit',
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
									setTooltipPosition({ x: 0, y: 0 })
									setHoveredElement(null)
								},
								// In a future, if we update our version of d3-selection this may
								// need to be updated to take arguments (MouseEvent, d) instead
								onMouseEnter: d => setHoveredElement(d.category),
							}}
							durationByAttr={{ fill: 0, stroke: 0 }}
							keyFn={(d) => d.category}
							duration={250}
						/>
					</DynamicWrapper>
					<AnimatedDataset
						dataset={datasetStackedByCategory}
						tag="line"
						init={{
							opacity: 0,
							[`${chartWidthDimension}1`]: chartWidthPaddingBefore - borderWidth.normal / 2,
							[`${chartWidthDimension}2`]: chartWidth - chartWidthPaddingAfter + borderWidth.normal / 2,
							[`${chartLengthDimension}1`]: isMobile ? chartLength - chartLengthPaddingAfter : 0,
							[`${chartLengthDimension}2`]: isMobile ? chartLength - chartLengthPaddingAfter : 0,
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
							[`${chartWidthDimension}1`]: chartWidthPaddingBefore - (isHomePageDesktopView ? borderWidth.normal : borderWidth.mobile) / 2,
							[`${chartWidthDimension}2`]: chartWidth - chartWidthPaddingAfter + (isHomePageDesktopView ? borderWidth.normal : borderWidth.mobile) / 2,
							[`${chartLengthDimension}1`]: (d) =>
								chartLength - lengthScale(d.startingPoint) + computeBarHeight(d.startingPoint, d.endPoint),
							[`${chartLengthDimension}2`]: (d) =>
								chartLength - lengthScale(d.startingPoint) + computeBarHeight(d.startingPoint, d.endPoint),
							stroke: (d, i) =>
								hoveredElement === d.category
									? findColor(d.category)
									: hoveredElement !== null &&
										hoveredElement === nextCategory(datasetStackedByCategory, i)
									? findColor(nextCategory(datasetStackedByCategory, i))
									: 'black',
							strokeWidth: isHomePageDesktopView ? borderWidth.normal + 1 : borderWidth.mobile,
							pointerEvents: 'none',
							shapeRendering: 'crispEdges',
						}}
						keyFn={(d) => d.category}
						duration={250}
						durationByAttr={{ fill: 0, stroke: 0 }}
					/>
					{isMobile ?
						// Text label inside of bars that displays on mobile
						(<>
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
													lengthScale(d.startingPoint) - lengthScale(d.endPoint) - paddingRect > minimumHeightText
											)
											.map((d) => d.category)
											.includes(d.category)
											? 1
											: 0,
									y: (d) =>
										height -
										lengthScale(d.startingPoint) +
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
													lengthScale(d.startingPoint) - lengthScale(d.endPoint) - paddingRect > minimumHeightText
											)
											.map((d) => d.category)
											.includes(d.category)
											? 1
											: 0,
									y: (d) =>
										height -
										lengthScale(d.startingPoint) +
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
						</>)
						:
						// X axis and legend only shown on desktop
						(<>
							{datasetCategoriesLabelsLegend
								.sort((a, b) => {
									const isFirst = hoveredElement === a.category
									const isSecond = hoveredElement === b.category
									if (isFirst) return 1
									else if (isSecond) return -1
									return 0
								})
								.map(d => (
									<g
										key={d.category}
										onMouseLeave={() => {
											setTooltipPosition({ x: 0, y: 0 })
											setHoveredElement(null)
										}}
										onClick={() => toggleSelectedCategory(d.category)}
										onMouseEnter={() => setHoveredElement(d.category)}
										cursor={interactive ? 'pointer' : 'inherit'}
										pointerEvents={interactive ? "auto" : "none"}
										tabIndex="0"
										role="button"
										aria-pressed={selectedElements.indexOf(d.category) >= 0}
									>
										<rect
											x={d.labelStartingX}
											y={d.labelStartingY}
											width={d.labelWidth}
											height={30}
											strokeWidth={hoveredElement === d.category ? borderWidth.normal : borderWidth.mobile}
											stroke={hoveredElement === d.category ? findColor(d.category) : 'black'}
											fill={hoveredElement === d.category || hoveredElement === null
												? (d.numberOfIncidents === 0 && hoveredElement !== d.category)
													? 'white'
													: findColor(d.category)
												: 'white'}
										/>
										<text
											x={d.labelStartingX + (d.labelWidth / 2)}
											y={d.labelStartingY + labelHeight / 2 + 1}
											textAnchor="middle"
											dominantBaseline="middle"
											{...textStyle}
										>
											{d.category}
										</text>
									</g>
								)
							)}
							<AnimatedDataset
								dataset={datasetStackedByCategory}
								init={{
									opacity: 0,
									y: height - paddings.bottom,
									x: 0,
								}}
								tag="text"
								attrs={{
									opacity: (d) => d.numberOfIncidents ? 1 : 0,
									y: height - paddings.bottom / 2,
									x: d => chartLength - lengthScale(d.startingPoint) + computeBarHeight(d.startingPoint, d.endPoint),
									textAnchor: 'end',
									...textStyle,
									pointerEvents: 'none',
									text: (d) => d.numberOfIncidents,
								}}
								keyFn={(d) => d.category}
								duration={250}
							/>
						</>)
					}
				</svg>
			</div>
		</>
	)
}
