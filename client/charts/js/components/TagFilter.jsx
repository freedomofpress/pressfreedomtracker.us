import React, { useContext } from 'react'
import * as d3 from 'd3'
import { flatMap, countBy } from 'lodash'
import {
	TOGGLE_PARAMETER_ITEM,
} from '../lib/actionTypes'
import { FiltersDispatch } from '../lib/context'
import CheckBoxBar from './CheckBoxBar'

const margins = {
	top: 10,
	left: 50,
	right: 30,
	bottom: 50,
}

export default function TagFilter({
	dataset,
	width,
	filterParameters: selectedTags,
}) {
	const updateFilters = useContext(FiltersDispatch);
	const tags = countBy(
		flatMap(dataset, 'tags')
	)

	const countTags = Object.entries(tags)
		.map(([tag, count]) => ({
			tag: tag,
			count: count,
		}))
		.sort((a, b) => b.count - a.count)
		.slice(0, 3)

	const xScale = d3
		.scaleLinear()
		.domain([0, d3.max(countTags.map((d) => d.count))])
		.range([margins.left, width - margins.right - margins.left])

	return (
		<div>
			{countTags.map(({ tag, count }, i) => {
				const isSelected = selectedTags.has(tag)
				return (
					<CheckBoxBar
						key={i}
						width={width-40}
						label={tag}
						count={count}
						barWidth={xScale(count)}
						isSelected={isSelected}
						index={i}
						onClick={() => {
							updateFilters({
								type: TOGGLE_PARAMETER_ITEM,
								payload: {
									filterName: 'tags',
									item: tag,
								}
							})
						}}
					/>
				)
			})}
		</div>
	)
}
