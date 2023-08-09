import React, { useEffect } from 'react'
import * as d3 from 'd3'

const averageLetterWidth = 8
const labelHeight = 30

const borderWidth = {
	hover: 7,
	normal: 5,
	mobile: 3,
}

export function calculateCategoriesLabelsLegend(datasetStackedByCategory, paddings, width) {
	return datasetStackedByCategory.reduce((acc, val) => {
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
}

export function calculateButtonsHeight(categoryButtonsLabels) {
	return d3.max(categoryButtonsLabels, d => d.labelStartingY) + labelHeight * 1.5
}

export default function CategoryButtons({
	interactive,
	categoryButtonsLabels,
	hoveredElement,
	setHoveredElement,
	toggleSelectedCategory = () => {},
	selectedElements = [],
	findColor,
	textStyle,
}) {
	const fillColor = (d) => {
		if (hoveredElement === d.category) return findColor(d.category)
		if (!hoveredElement && d.numberOfIncidents !== 0) return findColor(d.category)
		return "white"
	}

	return (<>
		{categoryButtonsLabels
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
						onMouseLeave={() => setHoveredElement(null)}
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
							fill={fillColor(d)}
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
		</>
		)
};
