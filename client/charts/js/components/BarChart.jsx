import React, { useState } from 'react'
import PropTypes from 'prop-types'
import * as d3 from 'd3'
import { AnimatedDataset } from 'react-animated-dataset'
import StaticDataset from './StaticDataset'
import DynamicWrapper from './DynamicWrapper'
import Slider from './Slider'
import Tooltip from './Tooltip'
import CategoryButtons, { calculateCategoriesLabelsLegend, calculateButtonsHeight } from './CategoryButtons.jsx'
import { computeMinimumNumberOfIncidents, stackDatasetByCategory } from './TreeMap'

const margins = {
	top: 0,
	left: 0,
	right: 2,
	bottom: 0,
}

const paddings = {
	left: 10,
	right: 10,
	bottom: 40,
	top: 40,
	mobile: 80,
}

const paddingsInternal = {
	left: 10,
	right: 40,
}

const borders = {
	normal: 5,
	hover: 7,
	grid: 1,
}

const textStyle = {
	fontFamily: 'var(--font-base)',
	fontWeight: '500',
	fontSize: '14px',
	lineHeight: '17px',
}

const textPadding = 10

/**
 * BarChart
 *
 * This component is in charge of rendering the bar chart components on the
 * frontend. This component can be used to render normal bar charts and
 * stacked bar charts in a variety of different combinations such as mobile
 * devices, header images, preview images, etc.
 */
export default function BarChart({
	data,
	allCategories,
	categoriesColors = {},
	categoryColumn,
	categoryDivider = ',',
	x,
	y,
	// A format function for the labels on the x-axis
	xFormat = x => x,
	// A format function for the labels on the y-axis
	yFormat = y => y,
	xDomain,
	yDomain,
	// An extra, optional format function for labels on the x-axis that show up
	// in the tooltip
	tooltipXFormat,
	titleLabel,
	isMobileView,
	width,
	height,
	id = '',
	numberOfTicks = 4,
	description,
	searchPageURL,
	// function prop received from ChartDownloader that binds the svg element to allow
	// it to be downloaded
	setSvgEl = () => {},
	interactive = true,
	disableAnimation = false,
}) {
	if (!data.length) return null
	const dataset = data.map((d, i) => ({ ...d, index: i }))

	// State to keep track of the current hovered element
	const [hoveredElement, setHoveredElement] = useState(null)
	const [sliderSelection, setSliderSelection] = useState(dataset[0].index)
	const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })

	const Dataset = disableAnimation ? StaticDataset : AnimatedDataset;

	const updateTooltipPosition = (MouseEvent) => {
		setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
	}

	// Calculate the space per label and only show every other label if too crowded
	const xDomainItems = xDomain || dataset.map((d) => d[x])
	const xLabelWidth = width / xDomainItems.length
	const xLabelDisplayInterval = xLabelWidth < 40 ? 2 : 1

	const minimumNumberOfIncidents = computeMinimumNumberOfIncidents(
		dataset,
		width,
		35
	)

	// Used when we have a stacked bar chart
	const datasetStackedByCategory = stackDatasetByCategory(
		dataset.map(d => ({ [categoryColumn]: Object.keys(d).join(', ') })),
		[],
		categoryColumn,
		categoryDivider,
		minimumNumberOfIncidents,
		allCategories
	)

	const categoryButtonsLabels = calculateCategoriesLabelsLegend(datasetStackedByCategory, paddings, width)
	const buttonsHeight = isMobileView || !allCategories
		? 0
		: calculateButtonsHeight(categoryButtonsLabels)

	const stackedData = d3.stack().keys(allCategories || [y])(dataset)

	const yScale = d3
		.scaleLinear()
		// Default to domain max 100 if there's no data
		.domain(yDomain || [0, d3.max(stackedData.flat(), d => d[1]) || 100])
		.range([height - (isMobileView ? paddings.mobile : paddings.bottom), paddings.top + buttonsHeight])
		.nice(numberOfTicks)

	const gridLines = yScale.ticks(numberOfTicks)

	const xScale = d3
		.scaleBand()
		.domain(xDomainItems)
		.range([paddings.left + paddingsInternal.left, width - paddings.right - paddingsInternal.right])
		.paddingInner(0.3)
		.paddingOuter(0.2)

	// xScaleOverLayer is for the bars that are only used for hover / click events,
	// this is similar to xScale, except that it does not leave gaps between bars
	// so that the closest bar is always hovered
	const xScaleOverLayer = d3
		.scaleBand()
		.domain(xDomainItems)
		.range([paddings.left + paddingsInternal.left, width - paddings.right - paddingsInternal.right])

	// Used for the Slider component on mobile devices where we are unable to label all of the points
	// due to space limitations
	const xSlider = d3
		.scalePoint()
		.domain(xDomainItems)
		.range([paddings.left, width - paddings.right])
		.padding(0.3)

	const computeBarheight = (y_) => {
		return height - yScale(y_) - (isMobileView ? paddings.mobile : paddings.bottom)
	}

	const findColor = (color) => categoriesColors[color] || 'white'
	const getBarColor = (key, data, defaultColor) => {
		const barColor = categoriesColors[key] || '#E07A5F'
		const isHoveredByDate = hoveredElement?.x === (tooltipXFormat || xFormat)(data[x])
		const isHoveredByKey = !hoveredElement?.x && hoveredElement?.y === key
		return isHoveredByDate || isHoveredByKey ? barColor : !hoveredElement ? barColor : defaultColor
	}

	const selectedElement = dataset.find((d) => d[x] === sliderSelection)
	const incidentsCount = selectedElement !== undefined ? selectedElement[y] : 0

	if (!width) return null

	// Desktop
	if (!isMobileView) {
		return (
			<>
				{hoveredElement?.x && interactive && (
					<Tooltip
						content={
							<div style={{ fontFamily: 'var(--font-base)', fontSize: 12, fontWeight: 500 }}>
								<div>Number of{
									(hoveredElement?.y && hoveredElement?.y !== 'count' && hoveredElement?.y !== 'numberOfIncidents') ? ` ${hoveredElement.y.replace('Incident', '')}` : ''
								} Incidents</div>
								<div
									style={{
										display: 'flex',
										justifyContent: 'space-between',
										gap: 15,
										marginTop: 8,
									}}
								>
									<div style={{ borderLeft: `solid 3px #E07A5F`, paddingLeft: 3 }}>
										{hoveredElement?.x}
									</div>
									<div>{yFormat(dataset.find((d) => (tooltipXFormat || xFormat)(d[x]) === hoveredElement?.x)[hoveredElement?.y || y])}</div>
								</div>
							</div>
						}
						x={tooltipPosition.x}
						y={tooltipPosition.y}
					/>
				)}
				<svg
					ref={setSvgEl}
					width="100%"
					aria-labelledby={id}
					style={{
						marginTop: margins.top,
						marginBottom: margins.bottom,
						marginRight: margins.right,
						marginLeft: margins.left,
						display: "block",
					}}
					viewBox={[0, 0, width, height]}
				>
					{description ? (<desc>{description}</desc>) : null}
					{allCategories && (
						<CategoryButtons
							interactive={interactive}
							categoryButtonsLabels={categoryButtonsLabels}
							hoveredElement={!hoveredElement?.x && hoveredElement?.y}
							setHoveredElement={(el) => setHoveredElement(el ? { y: el } : el)}
							findColor={findColor}
							textStyle={textStyle}
						/>
					)}
					<g>
						<Dataset
							dataset={gridLines}
							tag="line"
							init={{
								x1: (d) => (d === 0 ? 0 : paddings.left),
								x2: width - paddings.right,
								y1: height - paddings.bottom,
								y2: height - paddings.bottom,
							}}
							attrs={{
								x1: (d) => (d === 0 ? 0 : paddings.left),
								x2: width - paddings.right,
								y1: (d) => yScale(d),
								y2: (d) => yScale(d),
								stroke: 'black',
								strokeWidth: (d) => (d === 0 ? borders.normal : borders.grid),
								shapeRendering: 'crispEdges',
							}}
							duration={250}
							keyFn={(d) => d}
						/>
						<Dataset
							dataset={gridLines}
							tag="text"
							init={{
								opacity: 0,
								x: width - paddings.right,
								y: height - paddings.bottom,
							}}
							attrs={{
								opacity: 1,
								x: width - paddings.right,
								y: (d) => yScale(d) - textPadding,
								textAnchor: 'end',
								fontFamily: 'var(--font-mono)',
								fontSize: '12px',
								text: (d) => d,
							}}
							duration={250}
							keyFn={(d) => d}
						/>
					</g>
					{
						// These are the actual bars that are visibly displayed,
						// using animatedDataset to allow for load-in animations
						stackedData.map(branchBars => (
							<Dataset
								dataset={branchBars}
								tag="rect"
								init={{
									x: (d) => xScale(d.data[x]),
									y: height - paddings.bottom,
									height: 0,
									width: xScale.bandwidth(),
								}}
								attrs={{
									x: (d) => xScale(d.data[x]),
									y: (d) => yScale(d[1]),
									height: (d) => computeBarheight(d[1] - d[0]) || 0,
									width: xScale.bandwidth(),
									fill: (d) => getBarColor(branchBars.key, d.data, 'white'),
									strokeWidth: borders.normal,
									stroke: (d) => hoveredElement?.x ? getBarColor(branchBars.key, d.data, 'black') : 'black',
									cursor: (interactive && searchPageURL) ? 'pointer' : 'inherit',
									shapeRendering: 'crispEdges',
								}}
								duration={250}
								durationByAttr={{ fill: 0, stroke: 0 }}
								keyFn={(d) => branchBars.key + d.data.index}
								key={branchBars.key}
							/>
						))
					}
					{
						// These elements are for the hover and link targets,
						// they are not actually visibly displayed
						stackedData.map(branchBars => branchBars.map((branchEntry) => (
							<g
								key={branchBars.key + branchEntry.data.index}
								style={{ pointerEvents: interactive ? "auto" : "none" }}
							>
								<DynamicWrapper
									wrapperComponent={
										<a
											href={searchPageURL && searchPageURL(xFormat(branchEntry.data[x]))}
											role="link"
											aria-label={`${xFormat(branchEntry.data[x])}: ${yFormat(branchEntry.data[y])} ${titleLabel}`}
										/>
									}
									wrap={interactive && searchPageURL}
								>
									<rect
										x={xScaleOverLayer(branchEntry.data[x])}
										y={yScale(branchEntry[1])}
										height={computeBarheight(branchEntry[1] - branchEntry[0]) || 0}
										width={xScaleOverLayer.bandwidth()}
										style={{
											opacity: 0,
											cursor: (interactive && searchPageURL) ? 'pointer' : 'inherit',
										}}
										onMouseEnter={() => setHoveredElement({
											x: (tooltipXFormat || xFormat)(branchEntry.data[x]),
											y: branchBars.key
										})}
										onMouseMove={updateTooltipPosition}
										onMouseLeave={() => setHoveredElement(null)}
										shapeRendering="crispEdges"
									>
										<title>
											{`${xFormat(branchEntry.data[x])}: ${yFormat(branchEntry.data[y])} ${titleLabel}`}
										</title>
									</rect>
								</DynamicWrapper>
							</g>
						)))
					}
					<Dataset
						dataset={dataset.filter((d, i) => i % xLabelDisplayInterval === 0)}
						tag="text"
						init={{
							opacity: 0,
							x: (d) => (xScale(d[x]) !== undefined ? xScale(d[x]) + xScale.bandwidth() / 2 : 0),
							y: height - paddings.bottom / 2,
						}}
						attrs={{
							opacity: 1,
							x: (d) => (xScale(d[x]) !== undefined ? xScale(d[x]) + xScale.bandwidth() / 2 : 0),
							y: height - paddings.bottom / 2,
							textAnchor: 'middle',
							fill: (d) => (hoveredElement?.x === (tooltipXFormat || xFormat)(d[x]) ? '#E07A5F' : 'black'),
							fontFamily: 'var(--font-base)',
							fontWeight: 500,
							fontSize: '14px',
							text: (d) => xFormat(d[x]),
						}}
						duration={250}
						durationByAttr={{ fill: 0 }}
						keyFn={(d) => d.index}
					/>
				</svg>
			</>
		)
	}
	// Mobile
	else {
		return (
			<svg
				ref={setSvgEl}
				width="100%"
				viewBox={[0, 0, width, height]}
				style={{
					marginTop: margins.top,
					marginBottom: margins.bottom,
					marginRight: margins.right,
					marginLeft: margins.left,
				}}
				id="barchart-svg"
			>
				{description ? (<desc>{description}</desc>) : null}
				{
					// If there are multiple categories, ie a stacked bar chart,
					// we show the category buttons
					allCategories && (
						<CategoryButtons
							interactive={interactive}
							datasetStackedByCategory={datasetStackedByCategory}
							paddings={paddings}
							width={width}
							hoveredElement={!hoveredElement?.x && hoveredElement?.y}
							setHoveredElement={(el) => setHoveredElement(el ? { y: el } : el)}
							setButtonsHeight={setButtonsHeight}
							findColor={findColor}
							textStyle={textStyle}
						/>
					)
				}
				<g>
					<Dataset
						dataset={gridLines}
						tag="line"
						init={{
							opacity: 0,
						}}
						attrs={{
							opacity: 1,
							x1: (d) => (d === 0 ? 0 : paddings.left),
							x2: width - paddings.right,
							y1: (d) => yScale(d),
							y2: (d) => yScale(d),
							stroke: 'black',
							strokeWidth: (d) => (d === 0 ? borders.normal : borders.grid),
							shapeRendering: 'crispEdges',
						}}
						duration={250}
						keyFn={(d) => d}
					/>
					<Dataset
						dataset={gridLines}
						tag="text"
						init={{
							opacity: 0,
						}}
						attrs={{
							opacity: 1,
							x: width - paddings.right,
							y: (d) => yScale(d) - textPadding,
							textAnchor: 'end',
							fontFamily: 'var(--font-mono)',
							fontSize: '12px',
							text: (d) => d,
						}}
						duration={250}
						keyFn={(d) => d}
					/>
				</g>
				{stackedData.map(branchBars => (
					<DynamicWrapper
						key={branchBars.key}
						wrapperComponent={
							<a
								href={searchPageURL && searchPageURL(xFormat(branchBars[0].data[x]))}
								role="link"
								aria-label={`${xFormat(branchBars[0].data[x])}: ${yFormat(branchBars[0].data[y])} ${titleLabel}`}
							/>
						}
						wrap={searchPageURL}
					>
						<AnimatedDataset
							dataset={branchBars}
							tag="rect"
							init={{
								x: (d) => xScale(d.data[x]),
								y: height - paddings.mobile,
								height: 0,
								width: xScale.bandwidth(),
							}}
							attrs={{
								x: (d) => xScale(d.data[x]),
								y: (d) => yScale(d[1]),
								height: (d) => computeBarheight(d[1] - d[0]) || 0,
								width: xScale.bandwidth(),
								fill: (d) =>
									(sliderSelection === d.data[x] || (!hoveredElement?.x && hoveredElement?.y === branchBars.key))
										? getBarColor(branchBars.key, d.data, 'white')
										: sliderSelection === null
											? getBarColor(branchBars.key, d.data, 'white')
											: 'white',
								strokeWidth: borders.normal,
								stroke: (d) => (sliderSelection === d[x] ? '#E07A5F' : 'black'),
								cursor: searchPageURL ? 'pointer' : 'inherit',
								shapeRendering: 'crispEdges',
							}}
							duration={250}
							durationByAttr={{ fill: 0, stroke: 0 }}
							keyFn={(d) => branchBars.key + d.data.index}
							key={branchBars.key}
						/>
						<text
							x={width / 2}
							y={height - paddings.mobile / 2 - 7}
							textAnchor="middle"
							style={{
								fill: 'black',
								fontFamily: 'var(--font-base)',
								fontWeight: 500,
								fontSize: '14px',
							}}
						>
							{`${(tooltipXFormat || xFormat)(sliderSelection)}: ${incidentsCount} ${titleLabel}`}
						</text>
					</DynamicWrapper>
				))}
				<Slider
					elements={dataset.map((d) => d[x])}
					xScale={xSlider}
					y={height - paddings.bottom / 2}
					setSliderSelection={(d) => {
						setSliderSelection(d);
						setHoveredElement(null);
					}}
					sliderSelection={sliderSelection}
					idContainer={'barchart-svg'}
				/>
			</svg>
		)
	}
}

BarChart.propTypes = {
	data: PropTypes.array.isRequired,
	x: PropTypes.string.isRequired,
	y: PropTypes.string.isRequired,
	titleLabel: PropTypes.string.isRequired,
	isMobileView: PropTypes.bool.isRequired,
	width: PropTypes.number.isRequired,
	height: PropTypes.number.isRequired,
	numberOfTicks: PropTypes.number,
	searchPageURL: PropTypes.func,
}
