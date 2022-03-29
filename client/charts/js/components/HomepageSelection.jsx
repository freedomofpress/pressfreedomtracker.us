import React from 'react'
import * as d3 from 'd3'
import { sortBy } from 'lodash'
import ButtonsRow from './ButtonsRow'
import {
	filterDatasetByTag,
	filterDatasetByYear,
	filterDatasetByLastSixMonths,
	filterDatasetByFiltersApplied,
} from '../lib/utilities.js'

function chooseMostFrequentTags(dataset, numberOfTags) {
	const tags = dataset.map((d) => d.tags).filter((d) => d !== null)

	// Any incident having multiple tags is counted once per category
	const tagsSimplified = tags.flatMap((d) => d.split(',').map((e) => e.trim()))

	const incidentsCountByTag = sortBy(
		d3
			.rollups(
				tagsSimplified.map((d) => ({ tag: d })),
				(v) => v.length,
				(d) => d.tag
			)
			.map((d) => ({ tag: d[0], numberOfIncidents: d[1] })),
		(d) => -d.numberOfIncidents
	)

	return incidentsCountByTag.slice(0, numberOfTags).map((d) => d.tag)
}

export default function HomepageSelection({
	data: originalDataset,
	numberOfTags = 5,
	selectedTags = chooseMostFrequentTags(originalDataset, numberOfTags),
	currentDate = new Date(Date.UTC()),
	filtersApplied,
	setFiltersApplied,
}) {
	const years = d3
		.groups(
			originalDataset.map((d) => ({ year: d.date.getUTCFullYear() })),
			(d) => d.year
		)
		.map((d) => d[0])
		.sort((a, b) => b - a)

	function updateSelectedTag(label) {
		const tag = label === 'All incidents' ? null : label
		const newFiltersToApply = {
			tag: tag,
			year: filtersApplied.year,
			sixMonths: filtersApplied.sixMonths,
		}
		setFiltersApplied(newFiltersToApply)
	}

	function updateSelectedYear(label) {
		const newFiltersToApply = {
			tag: filtersApplied.tag,
			year: label === 'the past six months' ? null : label,
			sixMonths: label === 'the past six months',
		}

		setFiltersApplied(newFiltersToApply)
	}

	function isTagSelectable(originalDataset, tag, currentDate) {
		return (
			filterDatasetByFiltersApplied(
				originalDataset,
				{ tag: tag, year: filtersApplied.year, sixMonths: filtersApplied.sixMonths },
				currentDate
			).length > 0
		)
	}

	function isYearSelectable(originalDataset, year) {
		if (filtersApplied.tag !== null) {
			return (
				filterDatasetByYear(filterDatasetByTag(originalDataset, filtersApplied.tag), year).length >
				0
			)
		}
		return true
	}

	function isLastSixMonthsSelectable(originalDataset, currentDate) {
		if (filtersApplied.tag !== null) {
			return (
				filterDatasetByLastSixMonths(
					filterDatasetByTag(originalDataset, filtersApplied.tag),
					currentDate
				).length > 0
			)
		}
		return true
	}

	return (
		<div>
			<ButtonsRow
				label="Show data for"
				buttonLabels={['All incidents'].concat(selectedTags)}
				defaultSelection={'All incidents'}
				updateSelection={updateSelectedTag}
				isButtonSelectable={(tag) => {
					return tag === 'All incidents' || isTagSelectable(originalDataset, tag, currentDate)
				}}
			/>
			<ButtonsRow
				label="from"
				buttonLabels={['the past six months'].concat(years)}
				defaultSelection={'the past six months'}
				updateSelection={updateSelectedYear}
				isButtonSelectable={(year) => {
					return year === 'the past six months'
						? isLastSixMonthsSelectable(originalDataset, currentDate)
						: isYearSelectable(originalDataset, year)
				}}
			/>
		</div>
	)
}
