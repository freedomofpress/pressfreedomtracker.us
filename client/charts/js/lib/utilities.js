import * as d3 from 'd3'
import { uniq, debounce } from 'lodash'
import usStates from '../data/us-states-coordinates.json'

export const monthNames = [
	'Jan',
	'Feb',
	'Mar',
	'Apr',
	'May',
	'Jun',
	'Jul',
	'Aug',
	'Sep',
	'Oct',
	'Nov',
	'Dec',
]

export const monthIndexes = {
	Jan: 1,
	Feb: 2,
	Mar: 3,
	Apr: 4,
	May: 5,
	Jun: 6,
	Jul: 7,
	Aug: 8,
	Sep: 9,
	Oct: 10,
	Nov: 11,
	Dec: 12,
}


export const TIME_PRESETS = {
	SEVEN_DAYS: 'SEVEN_DAYS',
	FOUR_WEEKS: 'FOUR_WEEKS',
	TWELVE_WEEKS: 'TWELVE_WEEKS',
	SIX_MONTHS: 'SIX_MONTHS',
	ALL_TIME: 'ALL_TIME',
	YEAR: 'YEAR',
}


// These values are also set in sass at client/common/sass/_responsive.sass
export const mobileMax = 768;
export const tabletMax = 1152;
export const desktopMax = 1440;
export const tabletMin = mobileMax + 1;
export const desktopMin = tabletMax + 1;
export const tabletMinMainColumn = 500;

// Get the right calendar year for links, as 6mo view can span multiple
function yearForMonthClickInSixMonthsView(currentDate, monthNumber) {
	const windowStart = d3.utcMonth.offset(d3.utcMonth.floor(currentDate), -5)
	return (monthNumber - 1) >= windowStart.getUTCMonth()
		? windowStart.getUTCFullYear()
		: windowStart.getUTCFullYear() + 1
}

export function getFilteredUrl(databasePath, filtersApplied, currentDate, categories) {
	const categoriesSlugs = categories.reduce((acc, { title, slug }) => ({ ...acc, [title]: slug }), {})
	const origin = window.location.origin
	const baseUrl = filtersApplied.category === undefined || categoriesSlugs[filtersApplied.category] === undefined
		? `${origin}${databasePath}?`
		: `${origin}/${categoriesSlugs[filtersApplied.category]}/?`

	const parameters = []

	if (!!parseInt(filtersApplied.category)) {
		parameters.push(`categories=${filtersApplied.category}`)
	}

	if (filtersApplied.monthName !== undefined) {
		const monthNumber = monthIndexes[filtersApplied.monthName]
		const year = filtersApplied.timePreset === TIME_PRESETS.SIX_MONTHS
			? yearForMonthClickInSixMonthsView(currentDate, monthNumber)
			: filtersApplied.year
		const paddedMonthNumber = String(monthNumber).padStart(2, '0')
		const firstDayMonth = `${year}-${paddedMonthNumber}-01`
		const lastDayMonth = `${year}-${paddedMonthNumber}-${new Date(year, monthNumber, 0).getDate()}`
		parameters.push(`date_lower=${firstDayMonth}&date_upper=${lastDayMonth}`)
	}

	if (filtersApplied.state !== undefined) {
		parameters.push(`state=${filtersApplied.state.replace(' ', '+')}`)
	}

	if (filtersApplied.weekStart !== undefined && filtersApplied.weekEnd !== undefined) {
		parameters.push(`date_lower=${filtersApplied.weekStart}&date_upper=${filtersApplied.weekEnd}`)
	}

	if (filtersApplied.timePreset === TIME_PRESETS.YEAR && filtersApplied.monthName === undefined) {
		parameters.push(`date_lower=${filtersApplied.year}-01-01&date_upper=${filtersApplied.year}-12-31`)
	}

	if (filtersApplied.timePreset === TIME_PRESETS.SIX_MONTHS && filtersApplied.monthName === undefined) {
		const currentMonth = currentDate.getUTCMonth()
		const currentYear = currentDate.getUTCFullYear()

		const lastDate = new Date(currentYear, currentMonth + 1, 0)  // last day of the current month
		const firstDate = new Date(currentYear, currentMonth - 5, 1)  // first day of the month five months ago
		const firstDateFormatted = firstDate.toISOString().substring(0, 10)  // Extract the date portion of the ISO datetime
		const lastDateFormatted = lastDate.toISOString().substring(0, 10)

		parameters.push(`date_lower=${firstDateFormatted}&date_upper=${lastDateFormatted}`)
	}

	if (filtersApplied.tag !== undefined && filtersApplied.tag !== null) {
		parameters.push(`tags=${filtersApplied.tag.replace(' ', '+')}`)
	}

	return `${baseUrl}${parameters.join('&')}`
}

export function filterDatasetByTag(dataset, tag) {
	return dataset.filter(
		(d) =>
			d.tags &&
			d.tags
				.split(',')
				.map((s) => s.trim())
				.includes(tag)
	)
}

export function filterDatasetByYear(dataset, year) {
	return dataset.filter((d) => d.date.getUTCFullYear() === year)
}

// Filter to the last six months, inclusive on the *currentDate* end.
export function filterDatasetByLastSixMonths(dataset, currentDate) {
	const sixMonthsAgo = d3.utcMonth.offset(currentDate, -6)
	return dataset.filter(d => +d.date > +sixMonthsAgo && +d.date <= +currentDate)
}

// Rolling window ending with a partial period that contains currentDate.
function filterDatasetByLastNPeriods(dataset, currentDate, interval, numberOfPeriods) {
	const currentPeriodStart = interval.floor(currentDate)
	const firstPeriodStart = interval.offset(currentPeriodStart, -(numberOfPeriods - 1))
	return dataset.filter(d => +d.date >= +firstPeriodStart && +d.date <= +currentDate)
}

export function filterDatasetByLastNDays(dataset, currentDate, numberOfDays) {
	return filterDatasetByLastNPeriods(dataset, currentDate, d3.utcDay, numberOfDays)
}

export function filterDatasetByLastNWeeks(dataset, currentDate, numberOfWeeks) {
	return filterDatasetByLastNPeriods(dataset, currentDate, d3.utcMonday, numberOfWeeks)
}

export function resolveDefaultTimePreset(dataset, currentDate, sevenDayEnabled) {
	if (sevenDayEnabled && filterDatasetByLastNDays(dataset, currentDate, 7).length > 0) {
		return TIME_PRESETS.SEVEN_DAYS
	}
	if (dataset.length > 0 && filterDatasetByLastNWeeks(dataset, currentDate, 4).length === 0) {
		return TIME_PRESETS.SIX_MONTHS
	}
	return TIME_PRESETS.FOUR_WEEKS
}

export function filterDatasetByFiltersApplied(originalDataset, filtersApplied, currentDate) {
	const datasetFilteredByTag =
		filtersApplied.tag !== null
			? filterDatasetByTag(originalDataset, filtersApplied.tag)
			: originalDataset

	switch (filtersApplied.timePreset) {
		case TIME_PRESETS.SEVEN_DAYS:
			return filterDatasetByLastNDays(datasetFilteredByTag, currentDate, 7)
		case TIME_PRESETS.FOUR_WEEKS:
			return filterDatasetByLastNWeeks(datasetFilteredByTag, currentDate, 4)
		case TIME_PRESETS.TWELVE_WEEKS:
			return filterDatasetByLastNWeeks(datasetFilteredByTag, currentDate, 12)
		case TIME_PRESETS.SIX_MONTHS:
			return filterDatasetByLastSixMonths(datasetFilteredByTag, currentDate)
		case TIME_PRESETS.ALL_TIME:
			return datasetFilteredByTag
		case TIME_PRESETS.YEAR:
			return filterDatasetByYear(datasetFilteredByTag, filtersApplied.year)
	}
}

export function filterDatasets(
	dataset,
	filterCategories = [], // Array of valid categories or category
	filterTags = null, // Array or string of valid tags or tag
	dateRange = [null, null], // Array representing the min and max of dates to show
	filterStates = new Set(),
) {
	// Remove empty strings from filterCategories
	filterCategories = filterCategories.filter(d => d)

	// Create maps so that we don't have to do n^2 lookup times
	const filterCategoryMap = (Array.isArray(filterCategories) ? filterCategories : [filterCategories])
		.reduce((acc, val) => ({ ...acc, [val]: true }), {})
	const filterTagsMap = (Array.isArray(filterTags) ? filterTags : [filterTags])
		.reduce((acc, val) => ({ ...acc, [val]: true }), {})

	// Filter down to the categories and tags and date range we want
	return dataset
		.filter(({ categories, tags, date, state }) => {
			const incidentCategories = categories ? categories.split(',').map(d => d.trim()) : []
			const incidentTags = tags ? tags.split(',').map(d => d.trim()) : []

			const isExcludedCategory = filterCategories.length && !incidentCategories.find(c => filterCategoryMap[c])
			const isExcludedTag = filterTags && !incidentTags.find(c => filterTagsMap[c])
			const [startDateStr, endDateStr] = dateRange;
			const startDate = Date.parse(startDateStr)
			const endDate = Date.parse(endDateStr)
			const isBeforeStartDate = startDate && date < startDate
			const isAfterEndDate = endDate && date > endDate
			const isExcludedDate = isBeforeStartDate || isAfterEndDate
			const isExcludedState = filterStates.size > 0 && !filterStates.has(state)

			return !isExcludedCategory && !isExcludedTag && !isExcludedDate && !isExcludedState
		})
		.map(({ date, ...restProps }) => ({ ...restProps, date: d3.utcMonth.floor(date) }))
}

export function groupByMonthSorted(dataset, isLastSixMonths, currentDate) {
	const datasetGroupedByMonth = d3
		.groups(
			dataset.map((d) => ({ month: d.date.getUTCMonth() })),
			(d) => d.month
		)
		.map((d) => ({ month: d[0], monthName: monthNames[d[0]], numberOfIncidents: d[1].length }))

	const currentMonth = currentDate.getUTCMonth()
	const monthsConsidered =
		currentMonth < 5
			? monthNames.slice(currentMonth - 5).concat(monthNames.slice(0, currentMonth + 1))
			: monthNames.slice(currentMonth - 5, currentMonth + 1)

	// If yearly selection, we sort the array by month
	// If last six months selection, we sort the array based on the last six months
	const datasetGroupedByMonthSorted = isLastSixMonths
		? monthsConsidered
			.map((d) =>
				datasetGroupedByMonth.filter((e) => e.monthName === d).length === 0
					? { month: monthIndexes[d] - 1, monthName: d, numberOfIncidents: 0 }
					: datasetGroupedByMonth.filter((e) => e.monthName === d)
			)
			.flat()
		: monthNames
			.map((d) =>
				datasetGroupedByMonth.filter((e) => e.monthName === d).length === 0
					? { month: monthIndexes[d] - 1, monthName: d, numberOfIncidents: 0 }
					: datasetGroupedByMonth.filter((e) => e.monthName === d)
			)
			.flat()

	return datasetGroupedByMonthSorted
}

export function groupByYearsSorted(dataset) {
	const yearsGrouped = d3
		.groups(
			dataset.map((d) => ({ year: d.date.getUTCFullYear() })),
			(d) => d.year
		);
	// We get all the years so that we don't skip years with 0 incidents
	const yearsExtent = d3.extent(yearsGrouped, d => d[0])
	const yearsGroupedMapped = Object.fromEntries(yearsGrouped)
	const allYearsGrouped = d3.range(yearsExtent[0], yearsExtent[1] + 1)
		.map(year => [year, yearsGroupedMapped[year] || []])

	const datasetGroupedByYear = allYearsGrouped
		.map((d) => ({ year: d[0], numberOfIncidents: d[1].length }))

	return datasetGroupedByYear.sort((a, b) => a.year - b.year)
}

export function groupByDaysSorted(dataset, currentDate, numberOfDays) {
	const currentDayStart = d3.utcDay.floor(currentDate)
	const days = d3.range(numberOfDays).map((i) =>
		d3.utcDay.offset(currentDayStart, -(numberOfDays - 1 - i))
	)
	const formatWeekday = d3.utcFormat('%a')
	const formatLong = d3.utcFormat('%a, %b %-d')
	const formatIso = d3.utcFormat('%Y-%m-%d')

	return days.map((dayStart) => {
		const dayEnd = d3.utcDay.offset(dayStart, 1)
		const numberOfIncidents = dataset.filter((d) => {
			const t = +d.date
			return t >= +dayStart && t < +dayEnd
		}).length
		return {
			date: formatIso(dayStart),
			label: formatWeekday(dayStart),
			range: formatLong(dayStart),
			numberOfIncidents,
		}
	})
}

export function groupByWeeksSorted(dataset, currentDate, numberOfWeeks) {
	const currentWeekStart = d3.utcMonday.floor(currentDate)
	const weeks = d3.range(numberOfWeeks).map((i) =>
		d3.utcMonday.offset(currentWeekStart, -(numberOfWeeks - 1 - i))
	)
	const formatDay = d3.utcFormat('%b %-d')
	const formatIso = d3.utcFormat('%Y-%m-%d')

	return weeks.map((weekStart) => {
		const weekEnd = d3.utcDay.offset(d3.utcMonday.offset(weekStart, 1), -1)
		const numberOfIncidents = dataset.filter((d) => {
			const t = +d.date
			return t >= +weekStart && t <= +weekEnd
		}).length
		return {
			weekStart: formatIso(weekStart),
			weekEnd: formatIso(weekEnd),
			label: formatDay(weekStart),
			range: `${formatDay(weekStart)}–${formatDay(weekEnd)}`,
			numberOfIncidents,
		}
	})
}

export function groupByCity(dataset) {
	// Pick cities from dataset with coordinates
	const cities = dataset.map((d) => ({
		latitude: d.latitude,
		longitude: d.longitude,
		city: d.city,
		state: d.state !== undefined ? d.state : 'Abroad',
	}))

	// Group dataset by city and coordinates (some cities have the same name)
	// Reorganize the array as: [{latitude: .., longitude: .., name: .., numberOfIncidents: ..}, {..}, ...]
	// Sort the array to plot first the cities with the higher number of incidents
	const incidentsGroupedByCity = d3
		.flatRollup(
			cities,
			(v) => v.length,
			(d) => d.city,
			(d) => d.state,
			(d) => d.latitude,
			(d) => d.longitude
		)
		.map(([city, state, latitude, longitude, numberOfIncidents]) => ({
			city,
			state,
			latitude,
			longitude,
			numberOfIncidents,
		}))
		.sort((a, b) => b.numberOfIncidents - a.numberOfIncidents)

	// Remove rows without coordinates
	const incidentsGroupedFiltered = incidentsGroupedByCity.filter(
		(d) => d.latitude !== 'None' && d.longitude !== 'None'
	)

	if (incidentsGroupedByCity.length !== incidentsGroupedFiltered.length) {
		const citiesMissing = incidentsGroupedByCity - incidentsGroupedFiltered
		console.debug(`There are ${citiesMissing} cities without coordinates`)
	}

	return incidentsGroupedFiltered
}

export function groupByState(dataset) {
	const usStatesList = usStates.map((d) => d.acronym)

	// Pick cities from dataset with coordinates
	const states = dataset.map((d) => ({
		acronym: d.state !== undefined && usStatesList.includes(d.state) ? d.state : 'Abroad',
	}))

	// Group dataset by state
	// Sort the array to plot first the cities with the higher number of incidents
	const incidentsGroupedByState = d3
		.flatRollup(
			states,
			(v) => v.length,
			(d) => d.acronym
		)
		.map(([acronym, numberOfIncidents]) => ({
			state: acronym !== 'Abroad' ? usStates.find((d) => d.acronym === acronym).state : 'Abroad',
			usCode: acronym !== 'Abroad' ? acronym : null,
			numberOfIncidents,
			latitude:
				acronym !== 'Abroad' ? usStates.find((d) => d.acronym === acronym).latitude : undefined,
			longitude:
				acronym !== 'Abroad' ? usStates.find((d) => d.acronym === acronym).longitude : undefined,
		}))
		.sort((a, b) => b.numberOfIncidents - a.numberOfIncidents)

	return incidentsGroupedByState
}

export function countIncidentsOutsideUS(dataset) {
	const usStatesList = usStates.map((d) => d.acronym)
	// Added a quick hack to exclude Puerto Rico from the outside the US list
	// We should handle this more elegantly in the future
	return dataset.filter((d) => d.state === undefined || (!usStatesList.includes(d.state) && d.state !== 'PR')).length
}

export const categoriesColors = [
	'#669599', '#BAECF7', '#FBE0BC', '#F4C280', '#7EBBC8', '#B0829D',
	'#63729A', '#F9B29F', '#98C9CD', '#E2B6D0', '#B2B8E5',
]

// barChart Filter functions
export function firstDayOfMonth(date) {
	return d3.timeMonth.floor(new Date(date))
}

export function firstDayOfNextMonth(date) {
	return d3.timeMonth.ceil(new Date(date))
}

export function isSubset(subset, container) {
	// all elements of subset must be present in container
	return subset.every((element) => container.includes(element))
}

export const colors = [
	'#E07A5F',
	'#669599',
	'#B0829D',
	'#63729A',
	'#F4C280',
	'#7EBBC8',
	'#F9B29F',
	'#98C9CD',
	'#E2B6D0',
	'#B2B8E5',
	'#FBE0BC',
	'#BAECF7',
	'#975544',
	'#435556',
	'#6B5261',
	'#484B6B',
	'#957932',
	'#54767D',
]
export function removeElement(array, element) {
	return array.filter((d) => d !== element)
}

export function formatDataset(dataset) {
	return dataset
		.map((d) => ({
			...d,
			categories: uniq(d.categories?.split(',').map((c) => c.trim())) || [],
		}))
		.map((d) => ({
			...d,
			tags: uniq(d.tags?.split(',').map((c) => c.trim())) || [],
		}))
}

export function isDateValid(date) {
	return !Number.isNaN(new Date(date).getYear())
}


// Return a range of numbers, including both start and stop terms.
// rangeInclusive(0, 4, 1)  --> [0, 1, 2, 3, 4]
export function rangeInclusive(start, stop, step) {
	return Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + (i * step));
}


// Return a new set with elements of set A that are not in set B
export function difference(setA, setB) {
	const _difference = new Set(setA);
	for (const elem of setB) {
		_difference.delete(elem);
	}
	return _difference;
}

function trackMatomo(args = []) {
	if (typeof window._paq === 'object') _paq.push(['trackEvent', ...args]);
}

export const trackMatomoEvent = debounce(trackMatomo, 1000)
