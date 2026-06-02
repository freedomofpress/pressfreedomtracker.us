import {
	filterDatasetByYear,
	formatDataset,
	firstDayOfNextMonth,
	firstDayOfMonth,
	filterDatasetByTag,
	filterDatasetByLastSixMonths,
	filterDatasetByLastNDays,
	filterDatasetByLastNWeeks,
	resolveDefaultTimePreset,
	filterDatasetByFiltersApplied,
	groupByMonthSorted,
	groupByDaysSorted,
	groupByWeeksSorted,
	groupByCity,
	groupByState,
	countIncidentsOutsideUS,
	rangeInclusive, groupByYearsSorted,
	TIME_PRESETS,
} from '../lib/utilities'

describe(filterDatasetByTag, () => {
	test('filterDatasetByTag simple test', () => {
		expect(
			filterDatasetByTag([{ tags: 'test1' }, { tags: 'test2' }, { tags: 'test1' }], 'test1')
		).toEqual([{ tags: 'test1' }, { tags: 'test1' }])
	})

	test('filterDatasetByTag multiple tags', () => {
		expect(
			filterDatasetByTag(
				[{ tags: 'test1,test2,test3' }, { tags: 'test1,test3' }, { tags: 'test2' }],
				'test2'
			)
		).toEqual([{ tags: 'test1,test2,test3' }, { tags: 'test2' }])
	})

	test('filterDatasetByTag multiple tags and spaces', () => {
		expect(
			filterDatasetByTag(
				[{ tags: 'test1,  test2,  test3' }, { tags: 'test1,test3' }, { tags: 'test2' }],
				'test2'
			)
		).toEqual([{ tags: 'test1,  test2,  test3' }, { tags: 'test2' }])
	})

	test('filterDatasetByTag null tags', () => {
		expect(
			filterDatasetByTag(
				[{ tags: 'test1,  test2,  test3' }, { otherColumn: 1 }, { tags: 'test2' }],
				'test2'
			)
		).toEqual([{ tags: 'test1,  test2,  test3' }, { tags: 'test2' }])
	})
})

describe(filterDatasetByYear, () => {
	test('filterDatasetByYear simple case', () => {
		const x = filterDatasetByYear(
			[
				{ date: new Date(Date.UTC(2020, 1, 1)) },
				{ date: new Date(Date.UTC(2021, 1, 1)) },
				{ date: new Date(Date.UTC(2022, 1, 1)) },
				{ date: new Date(Date.UTC(2022, 1, 2)) },
			],
			2022
		)

		expect(x).toEqual([{ date: new Date(Date.UTC(2022, 1, 1)) }, { date: new Date(Date.UTC(2022, 1, 2)) }])
	})

	test('filterDatasetByYear complex dataset', () => {
		expect(
			filterDatasetByYear(
				[
					{ date: new Date(Date.UTC(2020, 1, 1)), column: 2 },
					{ date: new Date(Date.UTC(2021, 1, 1)), column: 3 },
					{ date: new Date(Date.UTC(2022, 1, 1)), column: 2 },
					{ date: new Date(Date.UTC(2022, 1, 2)), column: 4 },
				],
				2022
			)
		).toEqual([
			{ date: new Date(Date.UTC(2022, 1, 1)), column: 2 },
			{ date: new Date(Date.UTC(2022, 1, 2)), column: 4 },
		])
	})
})

describe(filterDatasetByLastSixMonths, () => {
	test('filterDatasetByLastSixMonths current date >= June', () => {
		expect(
			filterDatasetByLastSixMonths(
				[
					{ date: new Date(Date.UTC(2020, 0, 1)) },
					{ date: new Date(Date.UTC(2020, 1, 1)) },
					{ date: new Date(Date.UTC(2020, 2, 1)) },
					{ date: new Date(Date.UTC(2020, 3, 1)) },
					{ date: new Date(Date.UTC(2020, 4, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 6, 1)) },
					{ date: new Date(Date.UTC(2020, 7, 1)) },
					{ date: new Date(Date.UTC(2020, 8, 1)) },
					{ date: new Date(Date.UTC(2020, 9, 1)) },
					{ date: new Date(Date.UTC(2020, 10, 1)) },
					{ date: new Date(Date.UTC(2020, 11, 1)) },
					{ date: new Date(Date.UTC(2021, 0, 1)) },
					{ date: new Date(Date.UTC(2021, 1, 1)) },
					{ date: new Date(Date.UTC(2021, 2, 1)) },
					{ date: new Date(Date.UTC(2021, 3, 1)) },
					{ date: new Date(Date.UTC(2021, 4, 1)) },
					{ date: new Date(Date.UTC(2021, 5, 1)) },
				],
				new Date(Date.UTC(2021, 5, 1))
			)
		).toEqual([
			{ date: new Date(Date.UTC(2021, 0, 1)) },
			{ date: new Date(Date.UTC(2021, 1, 1)) },
			{ date: new Date(Date.UTC(2021, 2, 1)) },
			{ date: new Date(Date.UTC(2021, 3, 1)) },
			{ date: new Date(Date.UTC(2021, 4, 1)) },
			{ date: new Date(Date.UTC(2021, 5, 1)) },
		])
	})

	test('filterDatasetByLastSixMonths current date < June', () => {
		expect(
			filterDatasetByLastSixMonths(
				[
					{ date: new Date(Date.UTC(2020, 1, 1)) },
					{ date: new Date(Date.UTC(2020, 2, 1)) },
					{ date: new Date(Date.UTC(2020, 3, 1)) },
					{ date: new Date(Date.UTC(2020, 4, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 6, 1)) },
					{ date: new Date(Date.UTC(2020, 7, 1)) },
					{ date: new Date(Date.UTC(2020, 8, 1)) },
					{ date: new Date(Date.UTC(2020, 9, 1)) },
					{ date: new Date(Date.UTC(2020, 10, 1)) },
					{ date: new Date(Date.UTC(2020, 11, 1)) },
					{ date: new Date(Date.UTC(2020, 12, 1)) },
					{ date: new Date(Date.UTC(2021, 1, 1)) },
				],
				new Date(Date.UTC(2021, 1, 1))
			)
		).toEqual([
			{ date: new Date(Date.UTC(2020, 8, 1)) },
			{ date: new Date(Date.UTC(2020, 9, 1)) },
			{ date: new Date(Date.UTC(2020, 10, 1)) },
			{ date: new Date(Date.UTC(2020, 11, 1)) },
			{ date: new Date(Date.UTC(2020, 12, 1)) },
			{ date: new Date(Date.UTC(2021, 1, 1)) },
		])
	})

	test('filterDatasetByLastSixMonths elements present with date > current date', () => {
		expect(
			filterDatasetByLastSixMonths(
				[
					{ date: new Date(Date.UTC(2020, 1, 1)) },
					{ date: new Date(Date.UTC(2020, 2, 1)) },
					{ date: new Date(Date.UTC(2020, 3, 1)) },
					{ date: new Date(Date.UTC(2020, 4, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 6, 1)) },
					{ date: new Date(Date.UTC(2020, 7, 1)) },
					{ date: new Date(Date.UTC(2020, 8, 1)) },
					{ date: new Date(Date.UTC(2020, 9, 1)) },
					{ date: new Date(Date.UTC(2020, 10, 1)) },
					{ date: new Date(Date.UTC(2020, 11, 1)) },
					{ date: new Date(Date.UTC(2021, 0, 1)) },
				],
				new Date(Date.UTC(2020, 11, 1))
			)
		).toEqual([
			{ date: new Date(Date.UTC(2020, 6, 1)) },
			{ date: new Date(Date.UTC(2020, 7, 1)) },
			{ date: new Date(Date.UTC(2020, 8, 1)) },
			{ date: new Date(Date.UTC(2020, 9, 1)) },
			{ date: new Date(Date.UTC(2020, 10, 1)) },
			{ date: new Date(Date.UTC(2020, 11, 1)) },
		])
	})
})

describe(filterDatasetByLastNDays, () => {
	test('filterDatasetByLastNDays includes from lower boundary to currentDate inclusive', () => {
		// currentDate = Wed May 15 2024 12:00 UTC. 7-day window = May 9 (Thu) → May 15.
		const currentDate = new Date(Date.UTC(2024, 4, 15, 12, 0))
		expect(
			filterDatasetByLastNDays(
				[
					{ date: new Date(Date.UTC(2024, 4, 8, 23, 59)) },  // just before window
					{ date: new Date(Date.UTC(2024, 4, 9, 0, 0)) },    // window lower boundary
					{ date: new Date(Date.UTC(2024, 4, 12, 6, 0)) },   // middle
					{ date: new Date(Date.UTC(2024, 4, 15, 12, 0)) },  // currentDate
					{ date: new Date(Date.UTC(2024, 4, 15, 13, 0)) },  // just after currentDate
				],
				currentDate,
				7,
			)
		).toEqual([
			{ date: new Date(Date.UTC(2024, 4, 9, 0, 0)) },
			{ date: new Date(Date.UTC(2024, 4, 12, 6, 0)) },
			{ date: new Date(Date.UTC(2024, 4, 15, 12, 0)) },
		])
	})
})

describe(filterDatasetByLastNWeeks, () => {
	test('filterDatasetByLastNWeeks 4 weeks anchors on Monday', () => {
		// currentDate = Wed May 15 2024. Mon of that week = May 13.
		// 4-week window starts 3 weeks earlier = Mon Apr 22.
		const currentDate = new Date(Date.UTC(2024, 4, 15))
		expect(
			filterDatasetByLastNWeeks(
				[
					{ date: new Date(Date.UTC(2024, 3, 21)) },  // Sun Apr 21 — before Monday boundary
					{ date: new Date(Date.UTC(2024, 3, 22)) },  // Mon Apr 22 — window start
					{ date: new Date(Date.UTC(2024, 4, 13)) },  // Mon May 13
					{ date: new Date(Date.UTC(2024, 4, 15)) },  // currentDate
					{ date: new Date(Date.UTC(2024, 4, 16)) },  // after currentDate
				],
				currentDate,
				4,
			)
		).toEqual([
			{ date: new Date(Date.UTC(2024, 3, 22)) },
			{ date: new Date(Date.UTC(2024, 4, 13)) },
			{ date: new Date(Date.UTC(2024, 4, 15)) },
		])
	})

	test('filterDatasetByLastNWeeks 12 weeks anchors on Monday 11 weeks earlier', () => {
		// currentDate = Wed May 15 2024. 12-week window starts 11 weeks back from Mon May 13 = Mon Feb 26.
		const currentDate = new Date(Date.UTC(2024, 4, 15))
		expect(
			filterDatasetByLastNWeeks(
				[
					{ date: new Date(Date.UTC(2024, 1, 25)) },  // Sun Feb 25 — excluded
					{ date: new Date(Date.UTC(2024, 1, 26)) },  // Mon Feb 26 — included
					{ date: new Date(Date.UTC(2024, 4, 15)) },  // currentDate
				],
				currentDate,
				12,
			)
		).toEqual([
			{ date: new Date(Date.UTC(2024, 1, 26)) },
			{ date: new Date(Date.UTC(2024, 4, 15)) },
		])
	})
})

describe(groupByDaysSorted, () => {
	test('groupByDaysSorted returns N daily buckets with weekday labels and counts', () => {
		// currentDate = Wed May 15 2024. 7-day window: Thu May 9 → Wed May 15.
		const currentDate = new Date(Date.UTC(2024, 4, 15))
		const dataset = [
			{ date: new Date(Date.UTC(2024, 4, 9, 10, 0)) },   // Thu, +1
			{ date: new Date(Date.UTC(2024, 4, 9, 14, 0)) },   // Thu, +1
			{ date: new Date(Date.UTC(2024, 4, 12)) },          // Sun, +1
			{ date: new Date(Date.UTC(2024, 4, 15)) },          // Wed, +1
		]
		const result = groupByDaysSorted(dataset, currentDate, 7)
		expect(result).toHaveLength(7)
		expect(result[0]).toEqual({
			date: '2024-05-09',
			label: 'Thu',
			range: 'Thu, May 9',
			numberOfIncidents: 2,
		})
		expect(result[3]).toEqual({
			date: '2024-05-12',
			label: 'Sun',
			range: 'Sun, May 12',
			numberOfIncidents: 1,
		})
		expect(result[6]).toEqual({
			date: '2024-05-15',
			label: 'Wed',
			range: 'Wed, May 15',
			numberOfIncidents: 1,
		})
	})
})

describe(groupByWeeksSorted, () => {
	test('groupByWeeksSorted returns N Monday-starting buckets with range labels', () => {
		// currentDate = Wed May 15 2024. 4 weeks: Apr 22, Apr 29, May 6, May 13.
		const currentDate = new Date(Date.UTC(2024, 4, 15))
		const dataset = [
			{ date: new Date(Date.UTC(2024, 3, 22)) },  // Mon Apr 22 — week 1
			{ date: new Date(Date.UTC(2024, 3, 28)) },  // Sun Apr 28 — week 1
			{ date: new Date(Date.UTC(2024, 4, 13)) },  // Mon May 13 — week 4
		]
		const result = groupByWeeksSorted(dataset, currentDate, 4)
		expect(result).toHaveLength(4)
		expect(result[0]).toEqual({
			weekStart: '2024-04-22',
			weekEnd: '2024-04-28',
			label: 'Apr 22',
			range: 'Apr 22–Apr 28',
			numberOfIncidents: 2,
		})
		expect(result[3]).toEqual({
			weekStart: '2024-05-13',
			weekEnd: '2024-05-19',
			label: 'May 13',
			range: 'May 13–May 19',
			numberOfIncidents: 1,
		})
	})
})

describe(resolveDefaultTimePreset, () => {
	// currentDate = Wed May 15 2024. last 7 days starts Thu May 9; last 4 weeks starts Mon Apr 22.
	const currentDate = new Date(Date.UTC(2024, 4, 15))
	const withinSevenDays = { date: new Date(Date.UTC(2024, 4, 14)) }   // Tue May 14
	const withinFourWeeks = { date: new Date(Date.UTC(2024, 4, 1)) }    // Wed May 1 (not in last 7 days)
	const olderThanFourWeeks = { date: new Date(Date.UTC(2024, 2, 1)) } // Mar 1

	test('returns SEVEN_DAYS when enabled and there is data in the last 7 days', () => {
		expect(resolveDefaultTimePreset([withinSevenDays], currentDate, true))
			.toBe(TIME_PRESETS.SEVEN_DAYS)
	})

	test('ignores the 7-day window when not admin-enabled, even with recent data', () => {
		expect(resolveDefaultTimePreset([withinSevenDays], currentDate, false))
			.toBe(TIME_PRESETS.FOUR_WEEKS)
	})

	test('returns FOUR_WEEKS when enabled but no data in the last 7 days', () => {
		expect(resolveDefaultTimePreset([withinFourWeeks], currentDate, true))
			.toBe(TIME_PRESETS.FOUR_WEEKS)
	})

	test('widens to SIX_MONTHS when there is data but none in the last 4 weeks', () => {
		expect(resolveDefaultTimePreset([olderThanFourWeeks], currentDate, true))
			.toBe(TIME_PRESETS.SIX_MONTHS)
	})

	test('returns FOUR_WEEKS for an empty (still-loading) dataset', () => {
		expect(resolveDefaultTimePreset([], currentDate, true))
			.toBe(TIME_PRESETS.FOUR_WEEKS)
	})
})

describe(filterDatasetByFiltersApplied, () => {
	test('filterDatasetByFiltersApplied filter on year', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: new Date(Date.UTC(2020, 6, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 7, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 8, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 9, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 10, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 11, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 0, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 4, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 5, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 6, 1)), tags: 'test1' },
				],
				{ tag: null, year: 2021, timePreset: TIME_PRESETS.YEAR }
			)
		).toEqual([
			{ date: new Date(Date.UTC(2021, 0, 1)), tags: 'test1' },
			{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1' },
			{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1' },
			{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1' },
			{ date: new Date(Date.UTC(2021, 4, 1)), tags: 'test1' },
			{ date: new Date(Date.UTC(2021, 5, 1)), tags: 'test1' },
			{ date: new Date(Date.UTC(2021, 6, 1)), tags: 'test1' },
		])
	})

	test('filterDatasetByFiltersApplied filter on sixMonths', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: new Date(Date.UTC(2020, 6, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 7, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 8, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 9, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 10, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 11, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 12, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1,test2' },
					{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1, test2' },
					{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1, test2' },
					{ date: new Date(Date.UTC(2021, 4, 1)), tags: 'test1' },
				],
				{ tag: null, year: null, timePreset: TIME_PRESETS.SIX_MONTHS },
				new Date(Date.UTC(2021, 4, 1))
			)
		).toEqual([
			{ date: new Date(Date.UTC(2020, 11, 1)), tags: 'test1' },
			{ date: new Date(Date.UTC(2020, 12, 1)), tags: 'test1' },
			{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1,test2' },
			{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1, test2' },
			{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1, test2' },
			{ date: new Date(Date.UTC(2021, 4, 1)), tags: 'test1' },
		])
	})

	test('filterDatasetByFiltersApplied filter on tag', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: new Date(Date.UTC(2020, 6, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 7, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 8, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 9, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 10, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 11, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 12, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1,test2' },
					{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1, test2' },
					{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1, test2' },
					{ date: new Date(Date.UTC(2021, 4, 1)), tags: 'test1' },
				],
				{ tag: 'test2', year: null, timePreset: TIME_PRESETS.ALL_TIME },
				new Date(Date.UTC(2021, 4, 1))
			)
		).toEqual([
			{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1,test2' },
			{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1, test2' },
			{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1, test2' },
		])
	})

	test('filterDatasetByFiltersApplied filter on tag & sixMonths', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: new Date(Date.UTC(2020, 6, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 7, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 8, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 9, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 10, 1)), tags: 'test1,test2' },
					{ date: new Date(Date.UTC(2020, 11, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 12, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1,test2' },
					{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1, test2' },
					{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1, test2' },
					{ date: new Date(Date.UTC(2021, 4, 1)), tags: 'test1' },
				],
				{ tag: 'test2', year: null, timePreset: TIME_PRESETS.SIX_MONTHS },
				new Date(Date.UTC(2021, 4, 1))
			)
		).toEqual([
			{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1,test2' },
			{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1, test2' },
			{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1, test2' },
		])
	})

	test('filterDatasetByFiltersApplied filter on tag & year', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: new Date(Date.UTC(2020, 6, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 7, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 8, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 9, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 10, 1)), tags: 'test1,test2' },
					{ date: new Date(Date.UTC(2020, 11, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2020, 12, 1)), tags: 'test1' },
					{ date: new Date(Date.UTC(2021, 1, 1)), tags: 'test1,test2' },
					{ date: new Date(Date.UTC(2021, 2, 1)), tags: 'test1, test2' },
					{ date: new Date(Date.UTC(2021, 3, 1)), tags: 'test1, test2' },
					{ date: new Date(Date.UTC(2021, 4, 1)), tags: 'test1' },
				],
				{ tag: 'test2', year: 2020, timePreset: TIME_PRESETS.YEAR },
				new Date(Date.UTC(2021, 4, 1))
			)
		).toEqual([{ date: new Date(Date.UTC(2020, 10, 1)), tags: 'test1,test2' }])
	})
})

describe(groupByMonthSorted, () => {
	test('groupByMonthSorted simple test', () => {
		expect(
			groupByMonthSorted(
				[
					{ date: new Date(Date.UTC(2020, 0, 1)) },
					{ date: new Date(Date.UTC(2020, 1, 1)) },
					{ date: new Date(Date.UTC(2020, 2, 1)) },
					{ date: new Date(Date.UTC(2020, 3, 1)) },
					{ date: new Date(Date.UTC(2020, 4, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 6, 1)) },
					{ date: new Date(Date.UTC(2020, 7, 1)) },
					{ date: new Date(Date.UTC(2020, 8, 1)) },
					{ date: new Date(Date.UTC(2020, 9, 1)) },
					{ date: new Date(Date.UTC(2020, 10, 1)) },
					{ date: new Date(Date.UTC(2020, 11, 1)) },
				],
				false,
				new Date(Date.UTC(2020, 9, 1))
			)
		).toEqual([
			{ month: 0, monthName: 'Jan', numberOfIncidents: 1 },
			{ month: 1, monthName: 'Feb', numberOfIncidents: 1 },
			{ month: 2, monthName: 'Mar', numberOfIncidents: 1 },
			{ month: 3, monthName: 'Apr', numberOfIncidents: 1 },
			{ month: 4, monthName: 'May', numberOfIncidents: 1 },
			{ month: 5, monthName: 'Jun', numberOfIncidents: 3 },
			{ month: 6, monthName: 'Jul', numberOfIncidents: 1 },
			{ month: 7, monthName: 'Aug', numberOfIncidents: 1 },
			{ month: 8, monthName: 'Sep', numberOfIncidents: 1 },
			{ month: 9, monthName: 'Oct', numberOfIncidents: 1 },
			{ month: 10, monthName: 'Nov', numberOfIncidents: 1 },
			{ month: 11, monthName: 'Dec', numberOfIncidents: 1 },
		])
	})

	test('groupByMonthSorted missing elements', () => {
		expect(
			groupByMonthSorted(
				[
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 7, 1)) },
					{ date: new Date(Date.UTC(2020, 8, 1)) },
				],
				false,
				new Date(Date.UTC(2020, 9, 1))
			)
		).toEqual([
			{ month: 0, monthName: 'Jan', numberOfIncidents: 0 },
			{ month: 1, monthName: 'Feb', numberOfIncidents: 0 },
			{ month: 2, monthName: 'Mar', numberOfIncidents: 0 },
			{ month: 3, monthName: 'Apr', numberOfIncidents: 0 },
			{ month: 4, monthName: 'May', numberOfIncidents: 0 },
			{ month: 5, monthName: 'Jun', numberOfIncidents: 3 },
			{ month: 6, monthName: 'Jul', numberOfIncidents: 0 },
			{ month: 7, monthName: 'Aug', numberOfIncidents: 1 },
			{ month: 8, monthName: 'Sep', numberOfIncidents: 1 },
			{ month: 9, monthName: 'Oct', numberOfIncidents: 0 },
			{ month: 10, monthName: 'Nov', numberOfIncidents: 0 },
			{ month: 11, monthName: 'Dec', numberOfIncidents: 0 },
		])
	})

	test('groupByMonthSorted unordered dataset', () => {
		expect(
			groupByMonthSorted(
				[
					{ date: new Date(Date.UTC(2020, 7, 1)) },
					{ date: new Date(Date.UTC(2020, 8, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
				],
				false,
				new Date(Date.UTC(2020, 9, 1))
			)
		).toEqual([
			{ month: 0, monthName: 'Jan', numberOfIncidents: 0 },
			{ month: 1, monthName: 'Feb', numberOfIncidents: 0 },
			{ month: 2, monthName: 'Mar', numberOfIncidents: 0 },
			{ month: 3, monthName: 'Apr', numberOfIncidents: 0 },
			{ month: 4, monthName: 'May', numberOfIncidents: 0 },
			{ month: 5, monthName: 'Jun', numberOfIncidents: 3 },
			{ month: 6, monthName: 'Jul', numberOfIncidents: 0 },
			{ month: 7, monthName: 'Aug', numberOfIncidents: 1 },
			{ month: 8, monthName: 'Sep', numberOfIncidents: 1 },
			{ month: 9, monthName: 'Oct', numberOfIncidents: 0 },
			{ month: 10, monthName: 'Nov', numberOfIncidents: 0 },
			{ month: 11, monthName: 'Dec', numberOfIncidents: 0 },
		])
	})

	test('groupByMonthSorted last six months', () => {
		expect(
			groupByMonthSorted(
				[
					{ date: new Date(Date.UTC(2020, 3, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 7, 1)) },
					{ date: new Date(Date.UTC(2020, 8, 1)) },
				],
				true,
				new Date(Date.UTC(2020, 11, 1))
			)
		).toEqual([
			{ month: 6, monthName: 'Jul', numberOfIncidents: 0 },
			{ month: 7, monthName: 'Aug', numberOfIncidents: 1 },
			{ month: 8, monthName: 'Sep', numberOfIncidents: 1 },
			{ month: 9, monthName: 'Oct', numberOfIncidents: 0 },
			{ month: 10, monthName: 'Nov', numberOfIncidents: 0 },
			{ month: 11, monthName: 'Dec', numberOfIncidents: 0 },
		])
	})

	test('groupByMonthSorted last six months, next year', () => {
		expect(
			groupByMonthSorted(
				[
					{ date: new Date(Date.UTC(2020, 3, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 5, 1)) },
					{ date: new Date(Date.UTC(2020, 6, 1)) },
					{ date: new Date(Date.UTC(2020, 8, 1)) },
				],
				true,
				new Date(Date.UTC(2021, 1, 1))
			)
		).toEqual([
			{ month: 8, monthName: 'Sep', numberOfIncidents: 1 },
			{ month: 9, monthName: 'Oct', numberOfIncidents: 0 },
			{ month: 10, monthName: 'Nov', numberOfIncidents: 0 },
			{ month: 11, monthName: 'Dec', numberOfIncidents: 0 },
			{ month: 0, monthName: 'Jan', numberOfIncidents: 0 },
			{ month: 1, monthName: 'Feb', numberOfIncidents: 0 },
		])
	})
})

describe(groupByYearsSorted, () => {
	test('groupByYearsSorted test', () => {
		expect(
			groupByYearsSorted(
				[
					{ date: new Date(Date.UTC(2019, 0, 1)) },
					{ date: new Date(Date.UTC(2023, 1, 1)) },
					{ date: new Date(Date.UTC(2024, 2, 1)) },
				],
			)
		).toEqual([
			{ year: 2019, numberOfIncidents: 1 },
			{ year: 2020, numberOfIncidents: 0 },
			{ year: 2021, numberOfIncidents: 0 },
			{ year: 2022, numberOfIncidents: 0 },
			{ year: 2023, numberOfIncidents: 1 },
			{ year: 2024, numberOfIncidents: 1 },
		])
	})
})

describe(groupByCity, () => {
	test('groupByCity simple test', () => {
		expect(
			groupByCity([
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon' },
			])
		).toEqual([
			{ city: 'New York', latitude: 10, longitude: -10, state: 'New York', numberOfIncidents: 3 },
			{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon', numberOfIncidents: 1 },
		])
	})

	test('groupByCity latitude None', () => {
		expect(
			groupByCity([
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon' },
				{ city: 'Portland', latitude: 'None', longitude: 7, state: 'Oregon' },
			])
		).toEqual([
			{ city: 'New York', latitude: 10, longitude: -10, state: 'New York', numberOfIncidents: 3 },
			{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon', numberOfIncidents: 1 },
		])
	})

	test('groupByCity latitude Abroad', () => {
		expect(
			groupByCity([
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon' },
				{ city: 'Moscow', latitude: 50, longitude: 7 },
			])
		).toEqual([
			{ city: 'New York', latitude: 10, longitude: -10, state: 'New York', numberOfIncidents: 3 },
			{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon', numberOfIncidents: 1 },
			{ city: 'Moscow', latitude: 50, longitude: 7, state: 'Abroad', numberOfIncidents: 1 },
		])
	})

	test('groupByCity latitude Unordered', () => {
		expect(
			groupByCity([
				{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon' },
				{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
				{ city: 'New York', latitude: 10, longitude: -10, state: 'New York' },
			])
		).toEqual([
			{ city: 'New York', latitude: 10, longitude: -10, state: 'New York', numberOfIncidents: 3 },
			{ city: 'Portland', latitude: 9, longitude: 7, state: 'Oregon', numberOfIncidents: 2 },
		])
	})
})

describe(groupByState, () => {
	test('groupByState simple test', () => {
		expect(groupByState([{ state: 'AK' }, { state: 'AL' }, { state: 'AK' }])).toEqual([
			{ state: 'Alaska (AK)', usCode: 'AK', numberOfIncidents: 2, latitude: 63.588753, longitude: -154.493062 },
			{ state: 'Alabama (AL)', usCode: 'AL', numberOfIncidents: 1, latitude: 32.318231, longitude: -86.902298 },
		])
	})

	test('groupByState missing state', () => {
		expect(groupByState([{ state: 'AK' }, {}, { state: 'AK' }])).toEqual([
			{ state: 'Alaska (AK)', usCode: 'AK', numberOfIncidents: 2, latitude: 63.588753, longitude: -154.493062 },
			{ state: 'Abroad', usCode: null, numberOfIncidents: 1, latitude: undefined, longitude: undefined },
		])
	})

	test('groupByState unknown state', () => {
		expect(
			groupByState([
				{ state: 'AK' },
				{ state: 'AK' },
				{ state: 'Russia' },
				{ state: 'Finland' },
				{ state: 'AK' },
			])
		).toEqual([
			{ state: 'Alaska (AK)', usCode: 'AK', numberOfIncidents: 3, latitude: 63.588753, longitude: -154.493062 },
			{ state: 'Abroad', usCode: null, numberOfIncidents: 2, latitude: undefined, longitude: undefined },
		])
	})

	test('groupByState unordered dataset', () => {
		expect(groupByState([{ state: 'AL' }, { state: 'AK' }, { state: 'AK' }])).toEqual([
			{ state: 'Alaska (AK)', usCode: 'AK', numberOfIncidents: 2, latitude: 63.588753, longitude: -154.493062 },
			{ state: 'Alabama (AL)', usCode: 'AL', numberOfIncidents: 1, latitude: 32.318231, longitude: -86.902298 },
		])
	})
})

describe(countIncidentsOutsideUS, () => {
	test('countIncidentsOutsideUS simple test', () => {
		expect(countIncidentsOutsideUS([{ state: 'NY' }, {}])).toEqual(1)
	})

	test('countIncidentsOutsideUS undefined state', () => {
		expect(countIncidentsOutsideUS([{ state: 'NY' }, { state: undefined }])).toEqual(1)
	})

	test('countIncidentsOutsideUS unknown state', () => {
		expect(countIncidentsOutsideUS([{ state: 'NY' }, { state: 'Russia' }])).toEqual(1)
	})

	test('countIncidentsOutsideUS multiple cases', () => {
		expect(
			countIncidentsOutsideUS([{ state: 'NY' }, { state: undefined }, {}, { state: 'Russia' }])
		).toEqual(3)
	})
})

describe(formatDataset, () => {
	test('formatDataset categories trimming', () => {
		const x = formatDataset([{ categories: 'A,B' }, { categories: 'A,C' }, { categories: 'A,B,C' }])

		expect(x).toEqual([
			{ categories: ['A', 'B'], tags: [] },
			{ categories: ['A', 'C'], tags: [] },
			{ categories: ['A', 'B', 'C'], tags: [] },
		])
	})
	test('formatDataset tags trimming', () => {
		const x = formatDataset([{ tags: 'A,B' }, { tags: 'A,C' }, { tags: 'A,B,C' }])

		expect(x).toEqual([
			{ tags: ['A', 'B'], categories: [] },
			{ tags: ['A', 'C'], categories: [] },
			{ tags: ['A', 'B', 'C'], categories: [] },
		])
	})
	test('formatDataset tags and categories doubles handling', () => {
		const x = formatDataset([
			{ categories: 'A', tags: 'a' },
			{ categories: 'A,B,A,A,A,C', tags: 'a,b,c,d,c' },
		])

		expect(x).toEqual([
			{ categories: ['A'], tags: ['a'] },
			{ categories: ['A', 'B', 'C'], tags: ['a', 'b', 'c', 'd'] },
		])
	})
})

describe(firstDayOfNextMonth, () => {
	test('firstDayOfNextMonth', () => {
		const x = firstDayOfNextMonth(new Date('01-02-2022'))

		expect(x).toEqual(new Date('02-01-2022'))
	})
})

describe(rangeInclusive, () => {
	test('rangeInclusive', () => {
		const x = rangeInclusive(0, 4, 1)

		expect(x).toEqual([0, 1, 2, 3, 4])
	})

	test('rangeInclusive with step', () => {
		const x = rangeInclusive(0, 10, 3)

		expect(x).toEqual([0, 3, 6, 9])
	})
})


describe(firstDayOfMonth, () => {
	test('firstDayOfMonth', () => {
		const x = firstDayOfMonth(new Date('01-30-2022'))

		expect(x).toEqual(new Date('01-01-2022'))
	})
})
