import {
	filterDatasetByYear,
	formatDataset,
	firstDayOfNextMonth,
	firstDayOfMonth,
	filterDatasetByTag,
	filterDatasetByLastSixMonths,
	filterDatasetByFiltersApplied,
	groupByMonthSorted,
	groupByCity,
	groupByState,
	countIncidentsOutsideUS,
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
				{ date: '2020-01-01' },
				{ date: '2021-01-01' },
				{ date: '2022-01-01' },
				{ date: '2022-01-02' },
			],
			2022
		)

		expect(x).toEqual([{ date: '2022-01-01' }, { date: '2022-01-02' }])
	})

	test('filterDatasetByYear complex dataset', () => {
		expect(
			filterDatasetByYear(
				[
					{ date: '2020-01-01', column: 2 },
					{ date: '2021-01-01', column: 3 },
					{ date: '2022-01-01', column: 2 },
					{ date: '2022-01-02', column: 4 },
				],
				2022
			)
		).toEqual([
			{ date: '2022-01-01', column: 2 },
			{ date: '2022-01-02', column: 4 },
		])
	})
})

describe(filterDatasetByLastSixMonths, () => {
	test('filterDatasetByLastSixMonths current date >= June', () => {
		expect(
			filterDatasetByLastSixMonths(
				[
					{ date: '2020-01-01' },
					{ date: '2020-02-01' },
					{ date: '2020-03-01' },
					{ date: '2020-04-01' },
					{ date: '2020-05-01' },
					{ date: '2020-06-01' },
					{ date: '2020-07-01' },
					{ date: '2020-08-01' },
					{ date: '2020-09-01' },
					{ date: '2020-10-01' },
					{ date: '2020-11-01' },
					{ date: '2020-12-01' },
					{ date: '2021-01-01' },
					{ date: '2021-02-01' },
					{ date: '2021-03-01' },
					{ date: '2021-04-01' },
					{ date: '2021-05-01' },
					{ date: '2021-06-01' },
				],
				new Date(2021, 5, 1)
			)
		).toEqual([
			{ date: '2021-01-01' },
			{ date: '2021-02-01' },
			{ date: '2021-03-01' },
			{ date: '2021-04-01' },
			{ date: '2021-05-01' },
			{ date: '2021-06-01' },
		])
	})

	test('filterDatasetByLastSixMonths current date < June', () => {
		expect(
			filterDatasetByLastSixMonths(
				[
					{ date: '2020-01-01' },
					{ date: '2020-02-01' },
					{ date: '2020-03-01' },
					{ date: '2020-04-01' },
					{ date: '2020-05-01' },
					{ date: '2020-06-01' },
					{ date: '2020-07-01' },
					{ date: '2020-08-01' },
					{ date: '2020-09-01' },
					{ date: '2020-10-01' },
					{ date: '2020-11-01' },
					{ date: '2020-12-01' },
					{ date: '2021-01-01' },
				],
				new Date(2021, 1, 1)
			)
		).toEqual([
			{ date: '2020-08-01' },
			{ date: '2020-09-01' },
			{ date: '2020-10-01' },
			{ date: '2020-11-01' },
			{ date: '2020-12-01' },
			{ date: '2021-01-01' },
		])
	})

	test('filterDatasetByLastSixMonths elements present with date > current date', () => {
		expect(
			filterDatasetByLastSixMonths(
				[
					{ date: '2020-01-01' },
					{ date: '2020-02-01' },
					{ date: '2020-03-01' },
					{ date: '2020-04-01' },
					{ date: '2020-05-01' },
					{ date: '2020-06-01' },
					{ date: '2020-07-01' },
					{ date: '2020-08-01' },
					{ date: '2020-09-01' },
					{ date: '2020-10-01' },
					{ date: '2020-11-01' },
					{ date: '2020-12-01' },
					{ date: '2021-01-01' },
				],
				new Date(2020, 11, 1)
			)
		).toEqual([
			{ date: '2020-07-01' },
			{ date: '2020-08-01' },
			{ date: '2020-09-01' },
			{ date: '2020-10-01' },
			{ date: '2020-11-01' },
			{ date: '2020-12-01' },
		])
	})
})

describe(filterDatasetByFiltersApplied, () => {
	test('filterDatasetByFiltersApplied filter on year', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: '2020-06-01', tags: 'test1' },
					{ date: '2020-07-01', tags: 'test1' },
					{ date: '2020-08-01', tags: 'test1' },
					{ date: '2020-09-01', tags: 'test1' },
					{ date: '2020-10-01', tags: 'test1' },
					{ date: '2020-11-01', tags: 'test1' },
					{ date: '2020-12-01', tags: 'test1' },
					{ date: '2021-01-01', tags: 'test1' },
					{ date: '2021-02-01', tags: 'test1' },
					{ date: '2021-03-01', tags: 'test1' },
					{ date: '2021-04-01', tags: 'test1' },
					{ date: '2021-05-01', tags: 'test1' },
					{ date: '2021-06-01', tags: 'test1' },
				],
				{ tag: null, year: 2021, sixMonths: false }
			)
		).toEqual([
			{ date: '2021-01-01', tags: 'test1' },
			{ date: '2021-02-01', tags: 'test1' },
			{ date: '2021-03-01', tags: 'test1' },
			{ date: '2021-04-01', tags: 'test1' },
			{ date: '2021-05-01', tags: 'test1' },
			{ date: '2021-06-01', tags: 'test1' },
		])
	})

	test('filterDatasetByFiltersApplied filter on sixMonths', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: '2020-06-01', tags: 'test1' },
					{ date: '2020-07-01', tags: 'test1' },
					{ date: '2020-08-01', tags: 'test1' },
					{ date: '2020-09-01', tags: 'test1' },
					{ date: '2020-10-01', tags: 'test1' },
					{ date: '2020-11-01', tags: 'test1' },
					{ date: '2020-12-01', tags: 'test1' },
					{ date: '2021-01-01', tags: 'test1,test2' },
					{ date: '2021-02-01', tags: 'test1, test2' },
					{ date: '2021-03-01', tags: 'test1, test2' },
					{ date: '2021-04-01', tags: 'test1' },
				],
				{ tag: null, year: null, sixMonths: true },
				new Date(2021, 4, 1)
			)
		).toEqual([
			{ date: '2020-11-01', tags: 'test1' },
			{ date: '2020-12-01', tags: 'test1' },
			{ date: '2021-01-01', tags: 'test1,test2' },
			{ date: '2021-02-01', tags: 'test1, test2' },
			{ date: '2021-03-01', tags: 'test1, test2' },
			{ date: '2021-04-01', tags: 'test1' },
		])
	})

	test('filterDatasetByFiltersApplied filter on tag', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: '2020-06-01', tags: 'test1' },
					{ date: '2020-07-01', tags: 'test1' },
					{ date: '2020-08-01', tags: 'test1' },
					{ date: '2020-09-01', tags: 'test1' },
					{ date: '2020-10-01', tags: 'test1' },
					{ date: '2020-11-01', tags: 'test1' },
					{ date: '2020-12-01', tags: 'test1' },
					{ date: '2021-01-01', tags: 'test1,test2' },
					{ date: '2021-02-01', tags: 'test1, test2' },
					{ date: '2021-03-01', tags: 'test1, test2' },
					{ date: '2021-04-01', tags: 'test1' },
				],
				{ tag: 'test2', year: null, sixMonths: false },
				new Date(2021, 4, 1)
			)
		).toEqual([
			{ date: '2021-01-01', tags: 'test1,test2' },
			{ date: '2021-02-01', tags: 'test1, test2' },
			{ date: '2021-03-01', tags: 'test1, test2' },
		])
	})

	test('filterDatasetByFiltersApplied filter on tag & sixMonths', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: '2020-06-01', tags: 'test1' },
					{ date: '2020-07-01', tags: 'test1' },
					{ date: '2020-08-01', tags: 'test1' },
					{ date: '2020-09-01', tags: 'test1' },
					{ date: '2020-10-01', tags: 'test1,test2' },
					{ date: '2020-11-01', tags: 'test1' },
					{ date: '2020-12-01', tags: 'test1' },
					{ date: '2021-01-01', tags: 'test1,test2' },
					{ date: '2021-02-01', tags: 'test1, test2' },
					{ date: '2021-03-01', tags: 'test1, test2' },
					{ date: '2021-04-01', tags: 'test1' },
				],
				{ tag: 'test2', year: null, sixMonths: true },
				new Date(2021, 4, 1)
			)
		).toEqual([
			{ date: '2021-01-01', tags: 'test1,test2' },
			{ date: '2021-02-01', tags: 'test1, test2' },
			{ date: '2021-03-01', tags: 'test1, test2' },
		])
	})

	test('filterDatasetByFiltersApplied filter on tag & year', () => {
		expect(
			filterDatasetByFiltersApplied(
				[
					{ date: '2020-06-01', tags: 'test1' },
					{ date: '2020-07-01', tags: 'test1' },
					{ date: '2020-08-01', tags: 'test1' },
					{ date: '2020-09-01', tags: 'test1' },
					{ date: '2020-10-01', tags: 'test1,test2' },
					{ date: '2020-11-01', tags: 'test1' },
					{ date: '2020-12-01', tags: 'test1' },
					{ date: '2021-01-01', tags: 'test1,test2' },
					{ date: '2021-02-01', tags: 'test1, test2' },
					{ date: '2021-03-01', tags: 'test1, test2' },
					{ date: '2021-04-01', tags: 'test1' },
				],
				{ tag: 'test2', year: 2020, sixMonths: false },
				new Date(2021, 4, 1)
			)
		).toEqual([{ date: '2020-10-01', tags: 'test1,test2' }])
	})
})

describe(groupByMonthSorted, () => {
	test('groupByMonthSorted simple test', () => {
		expect(
			groupByMonthSorted(
				[
					{ date: '2020-01-01' },
					{ date: '2020-02-01' },
					{ date: '2020-03-01' },
					{ date: '2020-04-01' },
					{ date: '2020-05-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-07-01' },
					{ date: '2020-08-01' },
					{ date: '2020-09-01' },
					{ date: '2020-10-01' },
					{ date: '2020-11-01' },
					{ date: '2020-12-01' },
				],
				false,
				new Date(2020, 9, 1)
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
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-08-01' },
					{ date: '2020-09-01' },
				],
				false,
				new Date(2020, 9, 1)
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
					{ date: '2020-08-01' },
					{ date: '2020-09-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
				],
				false,
				new Date(2020, 9, 1)
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
					{ date: '2020-04-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-08-01' },
					{ date: '2020-09-01' },
				],
				true,
				new Date(2020, 11, 1)
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
					{ date: '2020-04-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-06-01' },
					{ date: '2020-08-01' },
					{ date: '2020-09-01' },
				],
				true,
				new Date(2021, 1, 1)
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
			{ state: 'Alaska (AK)', numberOfIncidents: 2, latitude: 63.588753, longitude: -154.493062 },
			{ state: 'Alabama (AL)', numberOfIncidents: 1, latitude: 32.318231, longitude: -86.902298 },
		])
	})

	test('groupByState missing state', () => {
		expect(groupByState([{ state: 'AK' }, {}, { state: 'AK' }])).toEqual([
			{ state: 'Alaska (AK)', numberOfIncidents: 2, latitude: 63.588753, longitude: -154.493062 },
			{ state: 'Abroad', numberOfIncidents: 1 },
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
			{ state: 'Alaska (AK)', numberOfIncidents: 3, latitude: 63.588753, longitude: -154.493062 },
			{ state: 'Abroad', numberOfIncidents: 2 },
		])
	})

	test('groupByState unordered dataset', () => {
		expect(groupByState([{ state: 'AL' }, { state: 'AK' }, { state: 'AK' }])).toEqual([
			{ state: 'Alaska (AK)', numberOfIncidents: 2, latitude: 63.588753, longitude: -154.493062 },
			{ state: 'Alabama (AL)', numberOfIncidents: 1, latitude: 32.318231, longitude: -86.902298 },
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
	test('formatDataset "/" space formatting', () => {
		const x = formatDataset([
			{ categories: 'A / B' },
			{ categories: 'A/B' },
			{ categories: 'A / B, C / D' },
			{ categories: 'A/B,C/D' },
		])

		expect(x).toEqual([
			{ categories: ['A/B'], tags: [] },
			{ categories: ['A/B'], tags: [] },
			{ categories: ['A/B', 'C/D'], tags: [] },
			{ categories: ['A/B', 'C/D'], tags: [] },
		])
	})
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

describe(firstDayOfMonth, () => {
	test('firstDayOfMonth', () => {
		const x = firstDayOfMonth(new Date('01-30-2022'))

		expect(x).toEqual(new Date('01-01-2022'))
	})
})
