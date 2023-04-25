import React, { useState } from 'react'
import PropTypes from 'prop-types'
import * as d3 from 'd3'
import { AnimatedDataset } from 'react-animated-dataset'
import Slider from './Slider'
import Tooltip from './Tooltip'

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

const textPadding = 10

export default function BarChart({
	data,
	x,
	y,
	xFormat = x => x,
	yFormat = y => y,
	xDomain,
	yDomain,
	tooltipXFormat,
	titleLabel,
	isMobileView,
	width,
	height,
	id = '',
	numberOfTicks = 4,
	description,
	openSearchPage,
	// function prop received from ChartDownloader that binds the svg element to allow
	// it to be downloaded
	setSvgEl = () => {},
}) {
	if (!data.length) return null
	const dataset = data.map((d, i) => ({ ...d, index: i }))

	const [hoveredElement, setHoveredElement] = useState(null)
	const [sliderSelection, setSliderSelection] = useState(dataset[0].index)
	const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })

	const updateTooltipPosition = (MouseEvent) => {
		setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
	}

	const yScale = d3
		.scaleLinear()
		// Default to domain max 100 if there's no data
		.domain(yDomain || [0, d3.max(dataset, (d) => d[y]) || 100])
		.range([height - (isMobileView ? paddings.mobile : paddings.bottom), paddings.top])
		.nice(numberOfTicks)

	const gridLines = yScale.ticks(numberOfTicks)

	const xScale = d3
		.scaleBand()
		.domain(xDomain || dataset.map((d) => d[x]))
		.range([paddings.left + paddingsInternal.left, width - paddings.right - paddingsInternal.right])
		.paddingInner(0.3)
		.paddingOuter(0.2)

	const xScaleOverLayer = d3
		.scaleBand()
		.domain(xDomain || dataset.map((d) => d[x]))
		.range([paddings.left + paddingsInternal.left, width - paddings.right - paddingsInternal.right])

	const xSlider = d3
		.scalePoint()
		.domain(xDomain || dataset.map((d) => d[x]))
		.range([0, width])
		.padding(0.3)

	const computeBarheight = (y_) => {
		return height - yScale(y_) - (isMobileView ? paddings.mobile : paddings.bottom)
	}

	const selectedElement = dataset.find((d) => d[x] === sliderSelection)
	const incidentsCount = selectedElement !== undefined ? selectedElement[y] : 0

	if (!width) return null

	if (!isMobileView) {
		return (
			<>
				{hoveredElement && (
					<Tooltip
						content={
							<div style={{ fontFamily: 'var(--font-base)', fontSize: 12, fontWeight: 500 }}>
								<div>Number of Incidents</div>
								<div
									style={{
										display: 'flex',
										justifyContent: 'space-between',
										gap: 15,
										marginTop: 8,
									}}
								>
									<div style={{ borderLeft: `solid 3px #E07A5F`, paddingLeft: 3 }}>
										{hoveredElement}
									</div>
									<div>{yFormat(dataset.find((d) => (tooltipXFormat || xFormat)(d[x]) === hoveredElement)[y])}</div>
								</div>
							</div>
						}
						x={tooltipPosition.x}
						y={tooltipPosition.y}
					/>
				)}
				<svg
					ref={setSvgEl}
					width={width}
					height={height}
					aria-labelledby={id}
					style={{
						marginTop: margins.top,
						marginBottom: margins.bottom,
						marginRight: margins.right,
						marginLeft: margins.left,
					}}
				>
					{description ? (<desc>{description}</desc>) : null}
					<g>
						<AnimatedDataset
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
						<AnimatedDataset
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
					<AnimatedDataset
						dataset={dataset}
						tag="rect"
						init={{
							x: (d) => xScale(d[x]),
							y: height - paddings.bottom,
							height: 0,
							width: xScale.bandwidth(),
						}}
						attrs={{
							x: (d) => xScale(d[x]),
							y: (d) => yScale(d[y]),
							height: (d) => computeBarheight(d[y]),
							width: xScale.bandwidth(),
							fill: (d) =>
								hoveredElement === (tooltipXFormat || xFormat)(d[x]) ? '#E07A5F' : hoveredElement === null ? '#E07A5F' : 'white',
							strokeWidth: borders.normal,
							stroke: (d) => (hoveredElement === (tooltipXFormat || xFormat)(d[x]) ? '#E07A5F' : 'black'),
							cursor: 'pointer',
							shapeRendering: 'crispEdges',
						}}
						duration={250}
						durationByAttr={{ fill: 0, stroke: 0 }}
						keyFn={(d) => d.index}
					/>
					{dataset.map((d) => (
						<g key={d[x]}>
							<rect
								x={xScaleOverLayer(d[x])}
								y={yScale(d[y])}
								height={computeBarheight(d[y])}
								width={xScaleOverLayer.bandwidth()}
								style={{
									opacity: 0,
									cursor: 'pointer',
								}}
								onMouseEnter={() => setHoveredElement((tooltipXFormat || xFormat)(d[x]))}
								onMouseMove={updateTooltipPosition}
								onMouseLeave={() => setHoveredElement(null)}
								onMouseUp={() => openSearchPage(xFormat(d[x]))}
								shapeRendering="crispEdges"
							>
								<title>
									{xFormat(d[x])}: {yFormat(d[y])} {titleLabel}
								</title>
							</rect>
						</g>
					))}
					<AnimatedDataset
						dataset={dataset}
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
							fill: (d) => (hoveredElement === (tooltipXFormat || xFormat)(d[x]) ? '#E07A5F' : 'black'),
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
	} else {
		return (
			<svg
				ref={setSvgEl}
				width={width}
				height={height}
				style={{
					marginTop: margins.top,
					marginBottom: margins.bottom,
					marginRight: margins.right,
					marginLeft: margins.left,
				}}
				id="barchart-svg"
			>
				{description ? (<desc>{description}</desc>) : null}
				<g>
					<AnimatedDataset
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
					<AnimatedDataset
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
				<AnimatedDataset
					dataset={dataset}
					tag="rect"
					attrs={{
						x: (d) => xScale(d[x]),
						y: (d) => yScale(d[y]),
						height: (d) => computeBarheight(d[y]),
						width: xScale.bandwidth(),
						fill: (d) =>
							sliderSelection === d[x] ? '#E07A5F' : sliderSelection === null ? '#E07A5F' : 'white',
						strokeWidth: borders.normal,
						stroke: (d) => (sliderSelection === d[x] ? '#E07A5F' : 'black'),
						cursor: 'pointer',
						shapeRendering: 'crispEdges',
					}}
					events={{
						onMouseUp: (mouseEvent, d) => openSearchPage(d[x]),
					}}
					duration={250}
					keyFn={(d) => d.index}
				/>
				<Slider
					elements={dataset.map((d) => d[x])}
					xScale={xSlider}
					y={height - paddings.bottom / 2}
					setSliderSelection={setSliderSelection}
					sliderSelection={sliderSelection}
					idContainer={'barchart-svg'}
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
					{`${sliderSelection}: ${incidentsCount} ${titleLabel}`}
				</text>
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
	openSearchPage: PropTypes.func,
}
