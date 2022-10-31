import React, { useContext, useState } from 'react'
import * as d3 from 'd3'
import { flatMap, countBy } from 'lodash'
import {
	TOGGLE_PARAMETER_ITEM,
	DELETE_PARAMETER_ITEMS,
} from '../lib/actionTypes'
import { FiltersDispatch } from '../lib/context'
import CheckBoxBar from './CheckBoxBar'
import AutoComplete from './Autocomplete'

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
	const updateFilters = useContext(FiltersDispatch)
	const [pickedTags, setPickedTags] = useState([])

	const tags = countBy(
		flatMap(dataset, 'tags')
	)

	const countTags = Object.entries(tags)
			.map(([tag, count]) => ({
				tag: tag,
				count: count,
			}))
			.sort((a, b) => b.count - a.count)

	const xScale = d3
			.scaleLinear()
			.domain([0, d3.max(countTags.map((d) => d.count))])
			.range([margins.left, width - margins.right - margins.left])

	// separate the tags into the top three (by incident count) and
	// the rest.
	let extendedTags = countTags.splice(3)

	// separate custom tags the user has picked from the rest into
	// their own list, the remove them from the rest.
	let pickedTagData = extendedTags.filter(({tag}) => pickedTags.includes(tag))
	extendedTags = extendedTags.filter(({tag}) => !pickedTags.includes(tag))

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
						barWidth={count > 0 ? xScale(count) : 0}
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
			{pickedTags.length > 0 && (
				<>
					<div className="filters__subheader">
						<span className="filter-widget--label">Your Picks</span>
						<button
							className="btn btn-ghost"
							onClick={() => {
								setPickedTags([])
								updateFilters({
									type: DELETE_PARAMETER_ITEMS,
									payload: {
										filterName: 'tags',
										payload: pickedTags,
									}
								})
							}}
						>
							Clear all
						</button>
					</div>
					{pickedTagData.map(({tag, count}, i) => {
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
				</>
			)}
			<AutoComplete
				suggestions={extendedTags}
				suggestionsLabelField="tag"
				suggestionsSidenoteField="count"
				name="tags"
				placeholder="Find tags..."
				itemNamePlural="tags"
				itemNameSingular="tag"
				handleSelect={(tag) => {
					setPickedTags(
						(previousPickedTags) => [...previousPickedTags, tag]
					)
					updateFilters({
						type: TOGGLE_PARAMETER_ITEM,
						payload: {
							filterName: 'tags',
							item: tag,
						}
					})
				}}
			/>

		</div>
	)
}
