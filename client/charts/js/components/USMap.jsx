import React, { useState } from 'react'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import { AnimatedDataset } from 'react-animated-dataset'
import us from '../data/us-states.json'
import Tooltip from './Tooltip'

const margins = {
	top: 0,
	left: 0,
	right: 0,
	bottom: 0,
}

const paddings = {
	left: 0,
	right: 40,
	bottom: 40,
	top: 0,
	text: 5,
	map: 50,
	textRight: 10,
	arrow: 20,
	arrowSmall: 13,
}

const markerSize = {
	min: 5,
	max: 30,
}

const markerBorder = {
	normal: 5,
	hover: 0,
	grid: 5,
	small: 1,
}

const mapBorder = {
	states: 0.457248,
	nation: 3,
}

export default function USMap({
	data: dataset,
	incidentsOutsideUS,
	width,
	height,
	id,
	openSearchPage,
	aggregationLocality = d => d.state,
	// function prop received from ChartDownloader that binds the svg element to allow
	// it to be downloaded
	setSvgEl = () => {},
}) {
	const [hoveredElement, setHoveredElement] = useState(null)
	const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })

	const updateTooltipPosition = (MouseEvent) => {
		setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
	}

	const path = d3.geoPath()
	const projection = d3.geoAlbersUsa().scale(1280).translate([480, 300])
	const hasLatLon = ({ latitude, longitude }) => latitude && longitude

	// Scale markers size depending on the number of incidents in a city
	const markerScale = d3.scaleSqrt().domain([0, 30]).range([markerSize.min, markerSize.max])

	if (!width) return null

	return (
		<>
			{hoveredElement && hoveredElement !== 'Abroad' && (
				<Tooltip
					content={
						<div style={{ fontFamily: 'var(--font-base)', fontSize: 12, fontWeight: 500 }}>
							<div>Number of Incidents</div>
							<div
								style={{ display: 'flex', justifyContent: 'space-between', gap: 15, marginTop: 8 }}
							>
								<div style={{ borderLeft: `solid 3px #E07A5F`, paddingLeft: 3 }}>
									{hoveredElement}
								</div>
								<div>
									{dataset.filter((d) => `${aggregationLocality(d)}` === hoveredElement).length !== 0
										? dataset.find((d) => `${aggregationLocality(d)}` === hoveredElement).numberOfIncidents
										: ''}
								</div>
							</div>
						</div>
					}
					x={tooltipPosition.x}
					y={tooltipPosition.y}
				/>
			)}
			<svg width={width} height={height} aria-labelledby={id} ref={setSvgEl}>
				<svg
					width={width}
					height={height - (paddings.bottom + paddings.top + paddings.map)}
					style={{
						marginTop: margins.top,
						marginBottom: margins.bottom,
						marginRight: margins.right,
						marginLeft: margins.left,
					}}
					viewBox={[0, 0, 975, 610]}
				>
					<g>
						{topojson.feature(us, us.objects.nation).features.map((d, i) => (
							<path
								style={{ stroke: 'black', strokeWidth: mapBorder.nation }}
								d={path(d)}
								key={i}
							/>
						))}
					</g>
					<g style={{ fill: '#ccc' }}>
						{topojson.feature(us, us.objects.states).features.map((d, i) => (
							<path
								style={{ fill: 'white', stroke: 'black', strokeWidth: mapBorder.states }}
								d={path(d)}
								key={i}
							/>
						))}
					</g>
					<g>
						<AnimatedDataset
							dataset={dataset.filter(hasLatLon)}
							tag="circle"
							init={{
								opacity: 0,
								r: 0,
								fill: (d) =>
									hoveredElement === null
										? '#E07A5F'
										: hoveredElement === `${aggregationLocality(d)}`
										? '#E07A5F'
										: 'white',
								strokeWidth: (d) =>
									hoveredElement === `${aggregationLocality(d)}` ? markerBorder.hover : markerBorder.normal,
							}}
							attrs={{
								opacity: 1,
								cx: (d) => projection([d.longitude, d.latitude])[0],
								cy: (d) => projection([d.longitude, d.latitude])[1],
								r: (d) => markerScale(d.numberOfIncidents),
								fill: (d) =>
									hoveredElement === null
										? '#E07A5F'
										: hoveredElement === `${aggregationLocality(d)}`
										? '#E07A5F'
										: 'white',
								stroke: 'black',
								strokeWidth: (d) =>
									hoveredElement === `${aggregationLocality(d)}` ? markerBorder.hover : markerBorder.normal,
							}}
							duration={250}
							durationByAttr={{ fill: 0, strokeWidth: 0 }}
							keyFn={(d) => `${aggregationLocality(d)}`}
						/>
					</g>
					<g>
						{dataset.filter(hasLatLon).map((d) => (
							<circle
								cx={projection([d.longitude, d.latitude])[0]}
								cy={projection([d.longitude, d.latitude])[1]}
								r={markerScale(d.numberOfIncidents) + 5}
								style={{ opacity: 0, cursor: 'pointer' }}
								onMouseMove={updateTooltipPosition}
								onMouseEnter={(mouseEvent) => {
									setHoveredElement(`${aggregationLocality(d)}`)
								}}
								onMouseLeave={() => {
									setHoveredElement(null)
								}}
								onMouseUp={(mouseEvent) => openSearchPage(d.usCode)}
								key={aggregationLocality(d)}
							/>
						))}
					</g>
				</svg>

				{incidentsOutsideUS && (
					<g>
						<rect
							x="0"
							y={
								height -
								paddings.bottom -
								paddings.text * 2 -
								markerBorder.grid -
								(width > 400 ? 14 : 12)
							}
							width={width}
							height={paddings.text * 2 + markerBorder.grid + (width > 400 ? 14 : 12)}
							fill="white"
							style={{
								cursor: 'pointer',
							}}
							onMouseEnter={() => setHoveredElement('Abroad')}
							onMouseOut={() => setHoveredElement(null)}
							onMouseUp={() => openSearchPage()}
						/>

						<AnimatedDataset
							dataset={['Incidents recorded outside of the US:']}
							tag="text"
							attrs={{
								x: hoveredElement === 'Abroad' ? paddings.text + 30 : paddings.text,
								y: height - paddings.bottom - paddings.text - markerBorder.grid,
								fontSize: width > 400 ? '14px' : '12px',
								fontFamily: 'var(--font-base)',
								cursor: 'pointer',
								fill: 'black',
								pointerEvents: 'none',
								text: (d) => d,
							}}
							keyFn={(d) => d}
							duration={300}
						/>
						<AnimatedDataset
							dataset={[String(incidentsOutsideUS)]}
							tag="text"
							attrs={{
								x: width - paddings.arrowSmall - (hoveredElement === 'Abroad' ? paddings.arrow : 95),
								y: height - paddings.bottom - paddings.text - markerBorder.grid - 1,
								fontSize: width > 400 ? 14 : 12,
								fontFamily: 'var(--font-base)',
								cursor: 'pointer',
								fill: 'black',
								textAnchor: 'end',
								pointerEvents: 'none',
								text: (d) => d,
							}}
							keyFn={(d) => d}
							duration={300}
							durationByAttr={{ fill: 0 }}
						/>

						<AnimatedDataset
							dataset={['']}
							tag="path"
							attrs={{
								d: 'M6 0.999999L12 7L6 13',
								stroke: 'black',
								fill: 'white',
								strokeWidth: 1,
								transform: `translate(${
									hoveredElement === 'Abroad' ? width - paddings.arrow : width - paddings.arrow - 50
								},${
									height -
									paddings.bottom -
									markerBorder.grid -
									paddings.text -
									(width > 400 ? 14 : 12) +
									1
								})`,
								opacity: hoveredElement === 'Abroad' ? 1 : 0,
								pointerEvents: 'none',
							}}
							duration={250}
						/>

						<AnimatedDataset
							dataset={['']}
							tag="line"
							attrs={{
								x1:
									hoveredElement === 'Abroad' ? width - paddings.arrow : width - paddings.arrow - 50,
								x2:
									12 +
									(hoveredElement === 'Abroad'
										? width - paddings.arrow
										: width - paddings.arrow - 50),
								y1:
									height -
									paddings.bottom -
									markerBorder.grid -
									paddings.text -
									(width > 400 ? 14 : 12) +
									8,
								y2:
									height -
									paddings.bottom -
									markerBorder.grid -
									paddings.text -
									(width > 400 ? 14 : 12) +
									8,
								stroke: 'black',
								opacity: hoveredElement === 'Abroad' ? 1 : 0,
								pointerEvents: 'none',
								shapeRendering: 'crispEdges',
							}}
							duration={250}
						/>

						<AnimatedDataset
							dataset={['']}
							tag="path"
							attrs={{
								d: 'M4 1L8 5L4 9',
								stroke: '#8F8F8F',
								fill: 'white',
								strokeWidth: 1,
								transform: `translate(${
									width - paddings.arrowSmall + 3 + (hoveredElement === 'Abroad' ? 150 : 0)
								},${
									height -
									paddings.bottom -
									markerBorder.grid -
									paddings.text -
									(width > 400 ? 14 : 12) +
									3
								})`,
								opacity: hoveredElement === 'Abroad' ? 0 : 1,
								pointerEvents: 'none',
							}}
							duration={250}
						/>

						<AnimatedDataset
							dataset={['']}
							tag="line"
							attrs={{
								x1: width - paddings.arrowSmall + 3 + (hoveredElement === 'Abroad' ? 150 : 0),
								x2: width - paddings.arrowSmall + 10 + (hoveredElement === 'Abroad' ? 150 : 0),
								y1:
									height -
									paddings.bottom -
									markerBorder.grid -
									paddings.text -
									(width > 400 ? 14 : 12) +
									8,
								y2:
									height -
									paddings.bottom -
									markerBorder.grid -
									paddings.text -
									(width > 400 ? 14 : 12) +
									8,
								stroke: '#8F8F8F',
								opacity: hoveredElement === 'Abroad' ? 0 : 1,
								pointerEvents: 'none',
								shapeRendering: 'crispEdges',
							}}
							duration={250}
						/>

						<AnimatedDataset
							dataset={['Go to incidents']}
							tag="text"
							attrs={{
								x: width - paddings.arrowSmall + (hoveredElement === 'Abroad' ? 150 : 0),
								opacity: hoveredElement === 'Abroad' ? 0 : 1,
								y: height - paddings.bottom - paddings.text - markerBorder.grid - 1,
								fontSize: width > 400 ? 13 : 11,
								fontFamily: 'var(--font-base)',
								cursor: 'pointer',
								fill: '#bdbdbd',
								textAnchor: 'end',
								text: (d) => d,
								pointerEvents: 'none',
							}}
							keyFn={(d) => d}
							duration={250}
						/>

						<line
							x1={0}
							x2={width}
							y1={
								height -
								paddings.bottom -
								paddings.text * 2 -
								markerBorder.grid -
								(width > 400 ? 14 : 12)
							}
							y2={
								height -
								paddings.bottom -
								paddings.text * 2 -
								markerBorder.grid -
								(width > 400 ? 14 : 12)
							}
							style={{ stroke: 'black', strokeWidth: markerBorder.small }}
							shapeRendering="crispEdges"
						/>
					</g>
				)}

				<line
					x1={0}
					x2={width}
					y1={height - paddings.bottom}
					y2={height - paddings.bottom}
					style={{ stroke: 'black', strokeWidth: markerBorder.grid }}
					shapeRendering="crispEdges"
				/>
			</svg>
		</>
	)
}
