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
	initialPickedTags,
	filterParameters: selectedTags,
}) {
	const updateFilters = useContext(FiltersDispatch)

	// "Picked" tags are ones the user has chosen from the extended
	// tag list, or via the URL parameters.  These will always be
	// displayed with a checkbox in the list, regardless of incident
	// count.
	const [pickedTags, setPickedTags] = useState(Array.from(initialPickedTags))

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

	// Remove any picked tags from the extended tags. Picked tags are
	// already part of the check box list and should not appear in the
	// drop-down chooser.
	extendedTags = extendedTags.filter(({tag}) => !pickedTags.includes(tag))

	// Compute what tags to display in the check box list: the top 3
	// tags (by incident count) plus all picked tags.
	let topTags = countTags.map(({tag}) => tag)
	let displayTags = countTags.concat(
		// Picked tags minus any that are already in the top 3, then
		// listed alongside their incident count (with zero as a
		// default).
		pickedTags.filter(tag => !topTags.includes(tag)).map(tag => ({count: tags[tag] ?? 0, tag}))
	)
	return (
		<div className="filters__form--fieldset">
			{displayTags.map(({ tag, count }, i) => {
				const isSelected = selectedTags.has(tag)
				return (
					<CheckBoxBar
						key={i}
						width={width-40}
						label={`#${tag}`}
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
