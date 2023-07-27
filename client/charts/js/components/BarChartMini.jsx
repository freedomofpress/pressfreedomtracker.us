import React from 'react'
import * as d3 from 'd3'

export default ({
	data,
	allCategories,
	categoriesColors = {},
	x,
	width = 655,
	height = 440,
}) => {
	const stackedData = d3.stack().keys(allCategories || [x])(data)

	const xScale = d3.scaleLinear().domain([0, d3.max(stackedData.flat(), d => d[1])]).range([0, width])

	const yHeight = height / data.length

	return (
		<svg
			viewBox={`0 0 ${width} ${height}`}
			width="100%"
			style={{ display: "block", marginBottom: "0.75rem", backgroundColor: "#fafafa" }}
		>
			{stackedData.map((branchBars) => branchBars.map((branchEntry, i) => (
				<rect
					key={`row-${i}`}
					x={xScale(branchEntry[0])}
					y={yHeight * i}
					width={xScale(branchEntry[1] - branchEntry[0])}
					height={yHeight}
					fill={categoriesColors[branchBars.key] || "#E07A5F"}
				/>
			)))}
		</svg>
	)
}
