import * as d3 from 'd3'
import React from 'react'
import { AnimatedDataset } from 'react-animated-dataset'

const margins = {
	top: 20,
	left: 1,
	right: 40,
	bottom: 1,
}

export default function BarChartYears({ width, height, countYears, selectedYears, onClick }) {
	const internalLeftMargin = 10
	const internalBottomMargin = 20
	const barsWidth = 10

	const xScale = d3
		.scaleLinear()
		.domain(d3.extent(countYears.map((d) => d.year)))
		.range([0 + margins.left + internalLeftMargin, width - margins.right])

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(countYears.map((d) => d.count))])
		.range([0, height - margins.bottom - margins.top])
		.nice()

	return (
		<div style={{ flexDirection: 'row', marginBottom: 10 }}>
			<svg
				width={width}
				height={height + internalBottomMargin}
				key={'BarChartYears'}
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

				{countYears.map((d, i) => (
					<g key={i}>
						<AnimatedDataset
							dataset={countYears}
							tag="rect"
							init={{
								height: 0,
								y: height,
							}}
							attrs={{
								x: (d) => xScale(d.year),
								y: (d) => height - margins.bottom - yScale(d.count),
								fill: (d) => 'black',
								width: barsWidth,
								stroke: 'black',
								strokeWidth: 2,
								height: (d) => yScale(d.count),
								key: (d) => d,
							}}
							events={{
								onClick: (_, d) => onClick(d),
							}}
							duration={250}
							keyFn={(d) => d.year}
						/>
						<text
							x={xScale(d.year) - internalLeftMargin}
							y={height + internalBottomMargin}
							style={{ fontSize: 12, fontFamily: 'var(--font-base)' }}
						>
							{d.year}
						</text>
					</g>
				))}
				<AnimatedDataset
					dataset={countYears}
					tag="rect"
					init={{
						height: 0,
						y: height,
					}}
					attrs={{
						x: (d) => xScale(d.year),
						y: (d) =>
							selectedYears.includes(d.year) ? height - margins.bottom - yScale(d.count) : height,
						fill: (d) => '#F2FC67',
						width: barsWidth,
						stroke: 'black',
						strokeWidth: 2,
						height: (d) => (selectedYears.includes(d.year) ? yScale(d.count) : 0),
						key: (d, i) => d,
					}}
					events={{
						onClick: (_, d) => onClick(d),
					}}
					duration={250}
					keyFn={(d) => d.year}
				/>
			</svg>
		</div>
	)
}
