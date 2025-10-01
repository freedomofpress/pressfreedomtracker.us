import React, { useState, useMemo } from 'react'
import * as d3 from 'd3'
import { AnimatedDataset } from 'react-animated-dataset'
import DynamicWrapper from './DynamicWrapper'
import Tooltip from './Tooltip'
import hexbinCoordinates from '../data/us-states-hexbin.json'

const SCALE_FACTOR = 0.95 // Scale the map size
const CONTRAST_THRESHOLD = 0.675; // Invert text when data is above 67% of the color scale

const margins = {
	top: 0,
	left: 0,
	right: 0,
	bottom: 0,
}

const defaultPaddings = {
	left: 0,
	right: 0,
	bottom: 40, // Align bottom borders with other homepage vizzes
	top: 22, // Adjust to avoid map cropping at various sizes
	text: 5,
	map: 0,
	textRight: 10,
	arrow: 20,
	arrowSmall: 13,
}

const hexBorder = {
	normal: 2.5,
	hover: 4,
	frame: 5,
	legend: 2,
}


export default function HexbinUSMap({
	data: dataset,
	description,
	incidentsOutsideUS,
	width,
	height,
	id,
	searchPageURL,
	aggregationLocality = d => d.state,
	addBottomBorder,
	overridePaddings = {},
	// function prop received from ChartDownloader that binds the svg element to allow
	// it to be downloaded
	setSvgEl = () => { },
	interactive = true,
	fullSize = true, // false for thumbnails/mini graphics
}) {
	const [hoveredElement, setHoveredElement] = useState(null)
	const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })

	const paddings = { ...defaultPaddings, ...overridePaddings }

	const updateTooltipPosition = (MouseEvent) => {
		setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
	}

	// Normalize state names for matching
	const normalizeStateName = (name) => {
		if (!name) return ''
		return name.replace(/\s*\([^)]*\)/, '').toLowerCase().trim()
	}

	// Create data lookup map and calculate max incidents
	const dataLookup = useMemo(() => {
		const lookup = new Map()
		dataset.forEach(d => {
			const locality = normalizeStateName(aggregationLocality(d))
			lookup.set(locality, d)
		})
		return lookup
	}, [dataset, aggregationLocality])

	const maxIncidents = useMemo(() =>
		d3.max(dataset, d => d.numberOfIncidents) || 1
	, [dataset])


	// Tweak color mapping for visual emphasis:
	const COLOR_BREAKS = [0, 0.1, 0.275, 0.65, 1];
	const COLOR_SCALE_EXPONENT = 0.85

	const colorScaleInterpolator = d3.scaleLinear()
		.domain(COLOR_BREAKS)
		.range(['#ffffff', '#F9E3C0', '#FFAA6D', '#ff5e00', '#842100'])
		.interpolate(d3.interpolateLab)

	const colorScale = d3.scaleSequentialPow(colorScaleInterpolator).exponent(COLOR_SCALE_EXPONENT).domain([0, maxIncidents])

	// Hexagon dimensions
	const hexWidth = Math.sqrt(3)
	const hexHeight = 2
	const hexVerticalSpacing = 0.75 // vertical overlap for tessellation
	const hexTopPadding = 0.25

	// Calculate bounds
	const minX = d3.min(hexbinCoordinates, d => d.x)
	const maxX = d3.max(hexbinCoordinates, d => d.x)
	const minY = d3.min(hexbinCoordinates, d => d.y)
	const maxY = d3.max(hexbinCoordinates, d => d.y)

	// Grid dimensions
	const gridWidth = (maxX - minX + 1) * hexWidth
	const gridHeight = (maxY - minY + 1) * hexHeight * hexVerticalSpacing + hexHeight * hexTopPadding

	const availableWidth = width - margins.left - margins.right - paddings.left - paddings.right
	const availableHeight = height - paddings.bottom - paddings.top - paddings.map

	const scale = Math.min(availableWidth / gridWidth, availableHeight / gridHeight) * SCALE_FACTOR
	const scaledHexRadius = scale

	const offsetX = (availableWidth - gridWidth * scale) / 2 + margins.left + paddings.left
	const offsetY = (availableHeight - gridHeight * scale) / 2 + margins.top + paddings.top

	// Generate pointy-top hexagon path
	const hexPath = useMemo(() => {
		const angles = []
		for (let i = 0; i < 6; i++) {
			// Pointy-top: start at 30°
			angles.push((Math.PI / 6) + (i * Math.PI / 3))
		}
		const points = angles.map(angle => [
			scaledHexRadius * Math.cos(angle),
			scaledHexRadius * Math.sin(angle)
		])
		return `M${points.map(p => p.join(',')).join('L')}Z`
	}, [scaledHexRadius])

	if (!width) return null

	return (
		<>
			{hoveredElement && interactive && hoveredElement !== 'Abroad' && (() => {
				const dataPoint = dataset.find((d) => `${aggregationLocality(d)}` === hoveredElement)
				const incidents = dataPoint ? (dataPoint.numberOfIncidents || 0) : 0
				const tooltipColor = incidents > 0 ? colorScale(incidents) : '#ccc'

				return (
					<Tooltip
						content={
							<div style={{ fontFamily: 'var(--font-base)', fontSize: 12, fontWeight: 500 }}>
								<div>Number of Incidents</div>
								<div
									style={{ display: 'flex', justifyContent: 'space-between', gap: 15, marginTop: 8 }}
								>
									<div style={{ borderLeft: `solid 3px ${tooltipColor}`, paddingLeft: 3 }}>
										{hoveredElement}
									</div>
									<div>
										{incidents}
									</div>
								</div>
							</div>
						}
						x={tooltipPosition.x}
						y={tooltipPosition.y}
					/>
				)
			})()}
			<svg
				width="100%"
				viewBox={`0 0 ${width} ${height}`}
				aria-labelledby={`${id}-title`}
				aria-describedby={description ? `${id}-desc` : undefined}
				role="img"
				ref={setSvgEl}
				style={{ display: 'block' }}
			>
				{description ? (<desc id={`${id}-desc`}>{description}</desc>) : null}

				{/* Render hexagons for each state */}
				<g role="list" aria-label="US states with incident data">
					{hexbinCoordinates.sort((a, b) => {
							// Sort states with data to back so they render after empty states in the DOM. This Ensures
							// light-gray borders don't render over black borders as canvg doesn't support blend modes.
							const getIncidents = (hexState) => (dataLookup.get(normalizeStateName(hexState.state)) || dataLookup.get(hexState.acronym.toLowerCase()))?.numberOfIncidents || 0
							return (getIncidents(a) > 0) - (getIncidents(b) > 0)
						}).map((hexState) => {
						// Find matching data for this state using lookup map
						const normalizedName = normalizeStateName(hexState.state)
						const stateAcronym = hexState.acronym.toLowerCase()
						const dataPoint = dataLookup.get(normalizedName) || dataLookup.get(stateAcronym)

						// Calculate hex position using proper tessellation
						const col = hexState.x - minX
						const row = hexState.y - minY

						// Pointy-top hex tessellation: odd rows offset by half width
						const hexX = offsetX + col * hexWidth * scale + (row % 2 === 1 ? (hexWidth * 0.5) * scale : 0)
						const hexY = offsetY + row * hexHeight * hexVerticalSpacing * scale

						const incidents = dataPoint ? (dataPoint.numberOfIncidents || 0) : 0
						const fillColor = incidents > 0 ? colorScale(incidents) : 'white'
						const stateName = dataPoint ? `${aggregationLocality(dataPoint)}` : hexState.state
						const isHovered = interactive && hoveredElement === stateName
						const strokeColor = incidents > 0 || isHovered ? '#000' : '#ccc'
						const strokeWidth = isHovered ? hexBorder.hover : hexBorder.normal
						const textColor = incidents > 0 ? (incidents > maxIncidents * CONTRAST_THRESHOLD ? '#fff' : '#000') : '#767676'

						return (
							<g key={hexState.acronym}>
								<DynamicWrapper
									wrapperComponent={
										<a
											href={searchPageURL && dataPoint && searchPageURL(dataPoint.usCode)}
											role="link"
											aria-label={`${stateName}: ${incidents} incidents`}
											style={{
												mixBlendMode: 'darken' }
											}

										/>
									}
									wrap={interactive && searchPageURL && dataPoint}
								>
									<g
										style={{
											cursor: (interactive && searchPageURL && dataPoint) ? 'pointer' : 'inherit',
										}}
										onMouseMove={updateTooltipPosition}
										onMouseEnter={() => {
											setHoveredElement(stateName)
										}}
										onMouseLeave={() => {
											setHoveredElement(null)
										}}
									>
										<path
											d={hexPath}
											transform={`translate(${hexX}, ${hexY})`}
											fill={fillColor}
											stroke={strokeColor}
											strokeWidth={strokeWidth}
											role="listitem"
											aria-label={`${stateName}: ${incidents} ${incidents === 1 ? 'incident' : 'incidents'}`}
										/>
										<text
											x={hexX}
											y={hexY}
											textAnchor="middle"
											dominantBaseline="central"
											fontSize={scaledHexRadius * 0.55}
											fontFamily="var(--font-base)"
											fontWeight="700"
											fill={textColor}
											pointerEvents="none"
											aria-hidden="true"
											style={{
												WebkitFontSmoothing: 'antialiased',
												MozOsxFontSmoothing: 'grayscale',
												textRendering: 'optimizeLegibility',
												textShadow: '0px 0px 2px rgba(255,255,255,0.25)',
											}}
										>
											{hexState.acronym}
										</text>
									</g>
								</DynamicWrapper>
							</g>
						)
					})}
				</g>


				{/* legend - hidden for thumbnails */}
				{maxIncidents > 0 && fullSize && (
					<g transform={`translate(${width - 120}, ${height - 120})`} role="img" aria-label="Legend: Color scale">
						<text
							x={0}
							y={0}
							fontSize="12"
							fontFamily="var(--font-base)"
							fill="#333"
							className='sr-only'
						>
							Number of incidents
						</text>
						<defs>
							<linearGradient id={`${id}-gradient`} x1="0%" y1="0%" x2="100%" y2="0%">
								{Array.from({ length: 11 }, (_, i) => {
									const value = (i / 10) * maxIncidents
									const offset = `${i * 10}%`
									return (
										<stop
											key={i}
											offset={offset}
											style={{
												stopColor: colorScale(value),
												stopOpacity: 1
											}}
										/>
									)
								})}
							</linearGradient>
						</defs>
						<rect
							x={0}
							y={10}
							width={100}
							height={10}
							fill={`url(#${id}-gradient)`}
							stroke="#333"
							strokeWidth={hexBorder.legend}
						/>
						<text
							x={0}
							y={32}
							fontSize="10"
							fontFamily="var(--font-base)"
							fill="#333"
						>
							0
						</text>
						{(() => {
							// We're using a non-linear scale. Adding accurately-positioned
							// values to the legend makes that more obvious.

							// First, find the values of 1/3 and 2/3 of the max:
							const oneThirdValue = Math.round(maxIncidents / 3)
							const twoThirdsValue = Math.round((maxIncidents / 3) * 2)
							// Then place at correct points on the legend:
							const oneThirdPosition = Math.pow(oneThirdValue / maxIncidents, COLOR_SCALE_EXPONENT) * 100
							const twoThirdsPosition = Math.pow(twoThirdsValue / maxIncidents, COLOR_SCALE_EXPONENT) * 100

							return (
								<>
									<text
										x={oneThirdPosition}
										y={32}
										fontSize="10"
										fontFamily="var(--font-base)"
										fill="#333"
										textAnchor="middle"
									>
										{oneThirdValue}
									</text>
									<text
										x={twoThirdsPosition}
										y={32}
										fontSize="10"
										fontFamily="var(--font-base)"
										fill="#333"
										textAnchor="middle"
									>
										{twoThirdsValue}
									</text>
								</>
							)
						})()}
						<text
							x={100}
							y={32}
							fontSize="10"
							fontFamily="var(--font-base)"
							fill="#333"
							textAnchor="end"
						>
							{maxIncidents}
						</text>
					</g>
				)}

				{incidentsOutsideUS && searchPageURL && (
					<g>
						{interactive ? (
							<a
								href={searchPageURL()}
								role="link"
								aria-label="Incidents recorded outside of the US"
							>
								<rect
									x="0"
									y={
										height -
										paddings.bottom -
										paddings.text * 2 -
										hexBorder.frame -
										(width > 400 ? 14 : 12)
									}
									width={width}
									height={paddings.text * 2 + hexBorder.frame + (width > 400 ? 14 : 12)}
									fill="white"
									style={{ cursor: 'pointer' }}
									onMouseEnter={() => setHoveredElement('Abroad')}
									onMouseOut={() => setHoveredElement(null)}
								/>
							</a>
						) : (
							<rect
								x="0"
								y={
									height -
									paddings.bottom -
									paddings.text * 2 -
									hexBorder.frame -
									(width > 400 ? 14 : 12)
								}
								width={width}
								height={paddings.text * 2 + hexBorder.frame + (width > 400 ? 14 : 12)}
								fill="white"
							/>
						)}

						<AnimatedDataset
							dataset={['Incidents recorded outside of the US:']}
							tag="text"
							attrs={{
								x: hoveredElement === 'Abroad' ? paddings.text + 30 : paddings.text,
								y: height - paddings.bottom - paddings.text - hexBorder.frame,
								fontSize: width > 400 ? '14px' : '12px',
								fontFamily: 'var(--font-base)',
								cursor: interactive ? 'pointer' : 'inherit',
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
								y: height - paddings.bottom - paddings.text - hexBorder.frame - 1,
								fontSize: width > 400 ? 14 : 12,
								fontFamily: 'var(--font-base)',
								cursor: interactive ? 'pointer' : 'inherit',
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
								transform: `translate(${hoveredElement === 'Abroad' ? width - paddings.arrow : width - paddings.arrow - 50
									},${height -
									paddings.bottom -
									hexBorder.frame -
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
									hexBorder.frame -
									paddings.text -
									(width > 400 ? 14 : 12) +
									8,
								y2:
									height -
									paddings.bottom -
									hexBorder.frame -
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
								transform: `translate(${width - paddings.arrowSmall + 3 + (hoveredElement === 'Abroad' ? 150 : 0)
									},${height -
									paddings.bottom -
									hexBorder.frame -
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
									hexBorder.frame -
									paddings.text -
									(width > 400 ? 14 : 12) +
									8,
								y2:
									height -
									paddings.bottom -
									hexBorder.frame -
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
								y: height - paddings.bottom - paddings.text - hexBorder.frame - 1,
								fontSize: width > 400 ? 13 : 11,
								fontFamily: 'var(--font-base)',
								cursor: interactive ? 'pointer' : 'inherit',
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
								hexBorder.frame -
								(width > 400 ? 14 : 12)
							}
							y2={
								height -
								paddings.bottom -
								paddings.text * 2 -
								hexBorder.frame -
								(width > 400 ? 14 : 12)
							}
							style={{ stroke: 'black', strokeWidth: hexBorder.legend }}
							shapeRendering="crispEdges"
						/>
					</g>
				)}

				{addBottomBorder ? (
					<line
						x1={0}
						x2={width}
						y1={height - paddings.bottom}
						y2={height - paddings.bottom}
						style={{ stroke: 'black', strokeWidth: hexBorder.frame }}
						shapeRendering="crispEdges"
					/>
				) : null}
			</svg>

		</>
	)
}
