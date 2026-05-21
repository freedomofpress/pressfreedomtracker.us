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
} from '../lib/utilities.js'

const TIME_LABELS = {
	SEVEN_DAYS: 'past 7 days',
	FOUR_WEEKS: 'past 4 weeks',
	TWELVE_WEEKS: 'past 12 weeks',
	SIX_MONTHS: 'past six months',
	ALL_TIME: 'all time',
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
		const presetLabels = Object.values(TIME_LABELS)
		const newFiltersToApply = {
			tag: filtersApplied.tag,
			year: presetLabels.includes(label) ? null : label,
			sixMonths: label === TIME_LABELS.SIX_MONTHS,
			allTime: label === TIME_LABELS.ALL_TIME,
			sevenDays: label === TIME_LABELS.SEVEN_DAYS,
			fourWeeks: label === TIME_LABELS.FOUR_WEEKS,
			twelveWeeks: label === TIME_LABELS.TWELVE_WEEKS,
		}

		setFiltersApplied(newFiltersToApply)
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

	function isLastNDaysSelectable(originalDataset, currentDate, numberOfDays) {
		if (filtersApplied.tag !== null) {
			return (
				filterDatasetByLastNDays(
					filterDatasetByTag(originalDataset, filtersApplied.tag),
					currentDate,
					numberOfDays
				).length > 0
			)
		}
		return true
	}

	function isLastNWeeksSelectable(originalDataset, currentDate, numberOfWeeks) {
		if (filtersApplied.tag !== null) {
			return (
				filterDatasetByLastNWeeks(
					filterDatasetByTag(originalDataset, filtersApplied.tag),
					currentDate,
					numberOfWeeks
				).length > 0
			)
		}
		return true
	}

	function isTimeButtonSelectable(year) {
		if (year === TIME_LABELS.SIX_MONTHS) {
			return isLastSixMonthsSelectable(originalDataset, currentDate)
		}
		if (year === TIME_LABELS.ALL_TIME) {
			return true
		}
		if (year === TIME_LABELS.SEVEN_DAYS) {
			return isLastNDaysSelectable(originalDataset, currentDate, 7)
		}
		if (year === TIME_LABELS.FOUR_WEEKS) {
			return isLastNWeeksSelectable(originalDataset, currentDate, 4)
		}
		if (year === TIME_LABELS.TWELVE_WEEKS) {
			return isLastNWeeksSelectable(originalDataset, currentDate, 12)
		}
		return isYearSelectable(originalDataset, year)
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
					...(sevenDayEnabled && isLastNDaysSelectable(originalDataset, currentDate, 7)
						? [TIME_LABELS.SEVEN_DAYS]
						: []),
					TIME_LABELS.FOUR_WEEKS,
					TIME_LABELS.TWELVE_WEEKS,
					TIME_LABELS.SIX_MONTHS,
					TIME_LABELS.ALL_TIME,
				]}
				dropDownLabels={years}
				defaultSelection={filtersApplied.sevenDays ? TIME_LABELS.SEVEN_DAYS : TIME_LABELS.FOUR_WEEKS}
				updateSelection={updateSelectedYear}
				isButtonSelectable={(year) => isTimeButtonSelectable(year)}
			/>
		</div>
	)
}
