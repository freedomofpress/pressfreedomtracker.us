import React from 'react'
import * as d3 from 'd3'
import { computeMinimumNumberOfIncidents, stackDatasetByCategory } from './TreeMap'
import { colors } from '../lib/utilities'

export default ({
	data,
	categoryColumn,
	allCategories,
	categoriesColors,
	width = 655,
	height = 440,
}) => {
	const minimumNumberOfIncidents = computeMinimumNumberOfIncidents(data, width, 0)

	const datasetStackedByCategory = stackDatasetByCategory(
		data, [], categoryColumn, ',', minimumNumberOfIncidents, allCategories
	)

	const getCategoryColour = (category) => {
		return categoriesColors[category]
	}

	const colorScale = categoriesColors !== undefined ? getCategoryColour : d3.scaleOrdinal(colors)

	const colorsByCategory = datasetStackedByCategory
		.map((d) => ({
			category: d.category,
			color: colorScale(d.category),
		}))

	const xScale = d3.scaleLinear()
		.domain([0, d3.max(datasetStackedByCategory, (d) => d.endPoint)])
		.range([0, width])

	const findColor = (cat) => colorsByCategory.find((d) => d.category === cat)?.color || "#EEEEEE"

	return (
		<svg
			viewBox={`0 0 ${width} ${height}`}
			width="100%"
			style={{ display: "block", marginBottom: "0.75rem" }}
		>
			{datasetStackedByCategory.map((row, i) => (
				<rect
					key={`row-${i}`}
					x={xScale(row.startingPoint)}
					y={0}
					width={xScale(row.endPoint) - xScale(row.startingPoint)}
					height={height}
					fill={findColor(row.category)}
				/>
			))}
		</svg>
	)
}
