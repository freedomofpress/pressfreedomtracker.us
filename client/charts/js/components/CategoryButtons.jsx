import React, { useEffect } from 'react'
import * as d3 from 'd3'

const averageLetterWidth = 8
const labelHeight = 30

const borderWidth = {
	hover: 7,
	normal: 5,
	mobile: 3,
}

export default function CategoryButtons({
	interactive,
	datasetStackedByCategory,
	paddings,
	width,
	hoveredElement,
	setHoveredElement,
	setButtonsHeight,
	toggleSelectedCategory = () => {},
	selectedElements = [],
	findColor,
	textStyle,
}) {
	// Calculate the positions of the rects for the legend
	const datasetCategoriesLabelsLegend = datasetStackedByCategory.reduce((acc, val) => {
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

	useEffect(() => {
		setButtonsHeight(
			d3.max(datasetCategoriesLabelsLegend, d => d.labelStartingY) + labelHeight * 1.5
		)
	})

	return (<>
		{datasetCategoriesLabelsLegend
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
							fill={hoveredElement === d.category || !hoveredElement
								? (d.numberOfIncidents === 0 && hoveredElement && hoveredElement !== d.category)
									? 'white'
									: findColor(d.category)
								: 'white'}
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
