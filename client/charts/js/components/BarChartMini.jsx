import React from 'react'
import * as d3 from 'd3'

export default ({
	data,
	x,
	width = 655,
	height = 440,
}) => {
	const xScale = d3.scaleLinear().domain([0, d3.max(data, d => d[x])]).range([0, width])

	const yHeight = height / data.length

	return (
		<svg
			viewBox={`0 0 ${width} ${height}`}
			width="100%"
			style={{ display: "block", marginBottom: "0.75rem" }}
		>
			{data.map((row, i) => (
				<rect
					key={`row-${i}`}
					x={0}
					y={yHeight * i}
					width={xScale(row[x])}
					height={yHeight}
					fill="#E07A5F"
				/>
			))}
		</svg>
	)
}
