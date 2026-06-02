import React from 'react'
import * as d3 from 'd3'
import { sortBy } from 'lodash'
import ButtonsRow from './ButtonsRow'
import {
	filterDatasetByTag,
	filterDatasetByYear,
	filterDatasetByLastSixMonths,
	filterDatasetByLastNDays,
	filterDatasetByLastNWeeks,
	filterDatasetByFiltersApplied,
	TIME_PRESETS,
} from '../lib/utilities.js'

const TIME_LABELS = {
	[TIME_PRESETS.SEVEN_DAYS]: 'past 7 days',
	[TIME_PRESETS.FOUR_WEEKS]: 'past 4 weeks',
	[TIME_PRESETS.TWELVE_WEEKS]: 'past 12 weeks',
	[TIME_PRESETS.SIX_MONTHS]: 'past six months',
	[TIME_PRESETS.ALL_TIME]: 'all time',
}

export function chooseTrendingTags(dataset, numberOfTags) {
	const currentDate = new Date();
	const filterStartDate = (new Date()).setFullYear(currentDate.getFullYear() - 1);
	const tags = dataset
		.filter(({ date }) => date >= filterStartDate)
		.map((d) => d.tags)
		.filter((d) => d !== null)

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
	selectedTags = chooseTrendingTags(originalDataset, numberOfTags),
	currentDate = new Date(),
	filtersApplied,
	setFiltersApplied,
	sevenDayEnabled = false,
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
			...filtersApplied,
			tag: tag,
		}
		setFiltersApplied(newFiltersToApply)
	}

	function updateSelectedYear(label) {
		if (typeof label === 'number') {
			setFiltersApplied({
				...filtersApplied,
				year: label,
				timePreset: TIME_PRESETS.YEAR,
			})
			return
		}
		const presetKey = Object.keys(TIME_LABELS).find((key) => TIME_LABELS[key] === label)
		setFiltersApplied({
			...filtersApplied,
			year: null,
			timePreset: presetKey ?? TIME_PRESETS.FOUR_WEEKS,
		})
	}

	function isTagSelectable(originalDataset, tag, currentDate) {
		return (
			filterDatasetByFiltersApplied(
				originalDataset,
				{ ...filtersApplied, tag },
				currentDate
			).length > 0
		)
	}

	function presetHasData(timeFilter) {
		const taggedDataset = filtersApplied.tag !== null
			? filterDatasetByTag(originalDataset, filtersApplied.tag)
			: originalDataset
		return timeFilter(taggedDataset).length > 0
	}

	function isTimeButtonSelectable(label) {
		switch (label) {
			case TIME_LABELS.SEVEN_DAYS: return presetHasData((d) => filterDatasetByLastNDays(d, currentDate, 7))
			case TIME_LABELS.FOUR_WEEKS: return presetHasData((d) => filterDatasetByLastNWeeks(d, currentDate, 4))
			case TIME_LABELS.TWELVE_WEEKS: return presetHasData((d) => filterDatasetByLastNWeeks(d, currentDate, 12))
			case TIME_LABELS.SIX_MONTHS: return presetHasData((d) => filterDatasetByLastSixMonths(d, currentDate))
			case TIME_LABELS.ALL_TIME: return true
			default: return presetHasData((d) => filterDatasetByYear(d, label))
		}
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
				tooltipIfUnselectable={'No incidents with this tag in specified date range'}
			/>
			<ButtonsRow
				label="from"
				buttonLabels={[
					...(sevenDayEnabled && isTimeButtonSelectable(TIME_LABELS.SEVEN_DAYS)
						? [TIME_LABELS.SEVEN_DAYS]
						: []),
					TIME_LABELS.FOUR_WEEKS,
					TIME_LABELS.TWELVE_WEEKS,
					TIME_LABELS.SIX_MONTHS,
					TIME_LABELS.ALL_TIME,
				]}
				dropDownLabels={years}
				defaultSelection={TIME_LABELS[filtersApplied.timePreset]}
				updateSelection={updateSelectedYear}
				isButtonSelectable={(year) => isTimeButtonSelectable(year)}
			/>
		</div>
	)
}
