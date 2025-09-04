import React, { useState } from 'react'
import * as d3 from 'd3'
import { AnimatedDataset } from 'react-animated-dataset'
import DynamicWrapper from './DynamicWrapper'
import Tooltip from './Tooltip'
import hexbinCoordinates from '../data/us-states-hexbin.json'

const SCALE_FACTOR = 0.95

const margins = {
	top: 20,
	left: 0,
	right: 0,
	bottom: 0,
}

const defaultPaddings = {
	left: 0,
	right: 0,
	bottom: 40,
	top: 0,
	text: 5,
	map: 0,
	textRight: 10,
	arrow: 20,
	arrowSmall: 13,
}

const hexBorder = {
	normal: 2.5,
	hover: 5,
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
}) {
	const [hoveredElement, setHoveredElement] = useState(null)
	const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })
	const [colorScheme, setColorScheme] = useState('interpolateReds')

	const paddings = { ...defaultPaddings, ...overridePaddings }

	const colorSchemes = {
		interpolateReds: {
			name: 'Reds',
			scale: d3.interpolateReds,
			type: 'interpolate'
		},
		interpolateYlOrRd: {
			name: 'YlOrRd',
			scale: d3.interpolateYlOrRd,
			type: 'interpolate'
		},
		schemeOrRd: {
			name: 'OrRd (9)',
			scale: d3.schemeOrRd[9],
			type: 'scheme'
		},
		schemeYlOrRd: {
			name: 'YlOrRd (9)',
			scale: d3.schemeYlOrRd[9],
			type: 'scheme'
		},
		schemeYlOrBr: {
			name: 'YlOrBr (9)',
			scale: d3.schemeYlOrBr[9],
			type: 'scheme'
		},
		interpolateRdPu: {
			name: 'RdPu',
			scale: d3.interpolateRdPu,
			type: 'interpolate'
		},
		interpolatePurples: {
			name: 'Purples',
			scale: d3.interpolatePurples,
			type: 'interpolate'
		},
		interpolateBuPu: {
			name: 'BuPu',
			scale: d3.interpolateBuPu,
			type: 'interpolate'
		},
		interpolatePuRd: {
			name: 'PuRd',
			scale: d3.interpolatePuRd,
			type: 'interpolate'
		}
	}

	const updateTooltipPosition = (mouseEvent) => {
		setTooltipPosition({ x: mouseEvent.clientX, y: mouseEvent.clientY })
	}

	// Create a mapping from state names to hexbin coordinates
	const stateToHexbin = {}
	hexbinCoordinates.forEach(state => {
		const stateName = state.state.replace(/\s*\([^)]*\)/, '')
		stateToHexbin[stateName] = state
		stateToHexbin[state.state] = state
		stateToHexbin[state.acronym] = state
	})

	// Scale incident values to hexagon colors
	const values = dataset.map((d) => d.numberOfIncidents)
	const maxIncidents = d3.max(values) || 1
	const currentScheme = colorSchemes[colorScheme]

	const colorScale = currentScheme.type === 'interpolate'
		? d3.scaleSequential(currentScheme.scale).domain([0, maxIncidents])
		: d3.scaleQuantize(currentScheme.scale).domain([0, maxIncidents])

	// Hexagon dimensions
	const hexWidth = Math.sqrt(3)
	const hexHeight = 2

	// Calculate bounds
	const minX = d3.min(hexbinCoordinates, d => d.x)
	const maxX = d3.max(hexbinCoordinates, d => d.x)
	const minY = d3.min(hexbinCoordinates, d => d.y)
	const maxY = d3.max(hexbinCoordinates, d => d.y)

	// Grid dimensions
	const gridWidth = (maxX - minX + 1) * hexWidth
	const gridHeight = (maxY - minY + 1) * hexHeight * 0.75 + hexHeight * 0.25

	const availableWidth = width - margins.left - margins.right - paddings.left - paddings.right
	const availableHeight = height - paddings.bottom - paddings.top - paddings.map

	const scale = Math.min(availableWidth / gridWidth, availableHeight / gridHeight) * SCALE_FACTOR
	const scaledHexRadius = scale

	const offsetX = (availableWidth - gridWidth * scale) / 2 + margins.left + paddings.left
	const offsetY = (availableHeight - gridHeight * scale) / 2 + margins.top + paddings.top

	// Generate flat-top hexagon path
	const generateHexPath = (radius) => {
		const angles = []
		for (let i = 0; i < 6; i++) {
			// Flat-top: start at 30°
			angles.push((Math.PI / 6) + (i * Math.PI / 3))
		}
		const points = angles.map(angle => [
			radius * Math.cos(angle),
			radius * Math.sin(angle)
		])
		return `M${points.map(p => p.join(',')).join('L')}Z`
	}

	const hexPath = generateHexPath(scaledHexRadius)


	if (!width) return null

	return (
		<>
			{hoveredElement && interactive && hoveredElement !== 'Abroad' && (
				<Tooltip
					content={
						<div style={{ fontFamily: 'var(--font-base)', fontSize: 12, fontWeight: 500 }}>
							<div>Number of Incidents</div>
							<div
								style={{ display: 'flex', justifyContent: 'space-between', gap: 15, marginTop: 8 }}
							>
								{(() => {
									const dataPoint = dataset.find((d) => `${aggregationLocality(d)}` === hoveredElement)
									const hexState = hexbinCoordinates.find(state => {
										const stateName = state.state.replace(/\s*\([^)]*\)/, '')
										return stateName === hoveredElement ||
											   state.acronym === hoveredElement ||
											   state.state === hoveredElement
									})

									const incidents = dataPoint ? (dataPoint.numberOfIncidents || 0) : 0
									const fillColor = incidents > 0 ? colorScale(incidents) : '#f0f0f0'

									return (
										<>
											<div style={{ borderLeft: `solid 3px ${fillColor}`, paddingLeft: 3 }}>
												{hoveredElement}
											</div>
											<div>
												{incidents}
											</div>
										</>
									)
								})()}
							</div>
						</div>
					}
					x={tooltipPosition.x}
					y={tooltipPosition.y}
				/>
			)}
			<svg
				width="100%"
				viewBox={`0 0 ${width} ${height}`}
				aria-labelledby={`${id}-title`}
				aria-describedby={description ? `${id}-desc` : undefined}
				role="img"
				ref={setSvgEl}
				style={{ display: 'block' }}
			>
				<title id={`${id}-title`}>United States Hexbin Map showing incidents by state</title>
				{description ? (<desc id={`${id}-desc`}>{description}</desc>) : null}

				{/* Render hexagons for each state */}
				<g role="list" aria-label="US states with incident data">
					{hexbinCoordinates.map((hexState) => {
						// Find matching data for this state
						const dataPoint = dataset.find(d => {
							const locality = `${aggregationLocality(d)}`.toLowerCase()
							const stateName = hexState.state.replace(/\s*\([^)]*\)/, '').toLowerCase()
							const stateAcronym = hexState.acronym.toLowerCase()

							// Exact matches only
							return locality === stateName ||
								   locality === stateAcronym ||
								   locality === hexState.state.toLowerCase()
						})

						// Show all states, even if they have no data (0 incidents)

						// Calculate hex position using proper tessellation
						const col = hexState.x - minX
						const row = hexState.y - minY

						// Flat-top hex tessellation: odd rows offset by half width
						const hexX = offsetX + col * hexWidth * scale + (row % 2 === 1 ? (hexWidth * 0.5) * scale : 0)
						const hexY = offsetY + row * hexHeight * 0.75 * scale

						const incidents = dataPoint ? (dataPoint.numberOfIncidents || 0) : 0
						const fillColor = incidents > 0 ? colorScale(incidents) : '#f0f0f0'
						const stateName = dataPoint ? `${aggregationLocality(dataPoint)}` : hexState.state
						const isHovered = hoveredElement === stateName
						const strokeColor = '#000'
						const strokeWidth = isHovered ? hexBorder.hover : hexBorder.normal

						return (
							<g key={hexState.acronym}>
								<DynamicWrapper
									wrapperComponent={
										<a
											href={searchPageURL && dataPoint && searchPageURL(dataPoint.usCode)}
											role="link"
											aria-label={`${stateName}: ${incidents} incidents`}
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
										onFocus={() => {
											setHoveredElement(stateName)
										}}
										onBlur={() => {
											setHoveredElement(null)
										}}
										onKeyDown={(e) => {
											if (e.key === 'Enter' || e.key === ' ') {
												e.preventDefault()
												if (interactive && searchPageURL && dataPoint) {
													window.location.href = searchPageURL(dataPoint.usCode)
												}
											}
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
											tabIndex={interactive ? "0" : undefined}
										/>
										<text
											x={hexX}
											y={hexY}
											textAnchor="middle"
											dominantBaseline="central"
											fontSize={scaledHexRadius * 0.55}
											fontFamily="var(--font-base)"
											fontWeight="700"
											fill={incidents > maxIncidents * 0.6 ? 'white' : 'black'}
											pointerEvents="none"
											aria-hidden="true"
											style={{
												WebkitFontSmoothing: 'antialiased',
												MozOsxFontSmoothing: 'grayscale',
												textRendering: 'optimizeLegibility'
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

				{/* Color scheme buttons */}
				{interactive && (
					<g transform="translate(20, 20)">
						{Object.entries(colorSchemes).map((entry, index) => {
							const [key, scheme] = entry
							const isSelected = colorScheme === key
							const buttonsPerRow = 3
							const buttonX = (index % buttonsPerRow) * 90
							const buttonY = Math.floor(index / buttonsPerRow) * 22

							return (
								<g key={key}>
									<rect
										x={buttonX}
										y={buttonY}
										width={85}
										height={18}
										fill={isSelected ? '#E07A5F' : '#f0f0f0'}
										stroke={isSelected ? '#333' : '#ccc'}
										strokeWidth={1}
										rx={2}
										style={{ cursor: 'pointer' }}
										onClick={() => setColorScheme(key)}
									/>
									<text
										x={buttonX + 42.5}
										y={buttonY + 12}
										textAnchor="middle"
										fontSize="10"
										fontFamily="var(--font-base)"
										fill={isSelected ? 'white' : '#333'}
										style={{ cursor: 'pointer', pointerEvents: 'none' }}
									>
										{scheme.name}
									</text>
								</g>
							)
						})}
					</g>
				)}

				{/* Color scale legend */}
				{maxIncidents > 0 && (
					<g transform={`translate(${width - 150}, 20)`}>
						<text
							x={0}
							y={0}
							fontSize="12"
							fontFamily="var(--font-base)"
							fill="#333"
						>
							Incidents
						</text>
						<defs>
							<linearGradient id={`${id}-gradient`} x1="0%" y1="0%" x2="100%" y2="0%">
								<stop offset="0%" style={{
									stopColor: currentScheme.type === 'interpolate'
										? currentScheme.scale(0)
										: currentScheme.scale[0],
									stopOpacity: 1
								}} />
								<stop offset="100%" style={{
									stopColor: currentScheme.type === 'interpolate'
										? currentScheme.scale(1)
										: currentScheme.scale[currentScheme.scale.length - 1],
									stopOpacity: 1
								}} />
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
								strokeWidth: hexBorder.legend,
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
								strokeWidth: hexBorder.legend,
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
