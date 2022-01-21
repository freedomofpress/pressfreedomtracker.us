import * as d3 from 'd3'

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
  return dataset.filter((d) => new Date(d.date).getFullYear() === year)
}

export function filterDatasetByLastSixMonths(dataset, currentDate) {
  const currentYear = currentDate.getFullYear()
  const currentMonth = currentDate.getMonth()
  if (currentMonth >= 5) {
    return dataset.filter(
      (d) =>
        new Date(d.date).getFullYear() === currentYear &&
        new Date(d.date).getMonth() >= currentMonth - 5
    )
  }
  const monthSixMonthsAgo = 11 - (5 - currentMonth)
  return dataset.filter(
    (d) =>
      new Date(d.date).getFullYear() === currentYear ||
      (new Date(d.date).getFullYear() === currentYear - 1 &&
        new Date(d.date).getMonth() >= monthSixMonthsAgo)
  )
}

export function filterDatasetByFiltersApplied(originalDataset, filtersApplied, currentDate) {
  const datasetFilteredByTag =
    filtersApplied.tag !== null
      ? filterDatasetByTag(originalDataset, filtersApplied.tag)
      : originalDataset
  const datasetFilteredByYear =
    filtersApplied.year !== null
      ? filterDatasetByYear(datasetFilteredByTag, filtersApplied.year)
      : datasetFilteredByTag
  const datasetFilteredBySixMonths =
    filtersApplied.sixMonths !== false
      ? filterDatasetByLastSixMonths(datasetFilteredByYear, currentDate)
      : datasetFilteredByYear

  return datasetFilteredBySixMonths
}

export function groupByMonthSorted(dataset, isLastSixMonths, currentDate) {
  const datasetGroupedByMonth = d3
    .groups(
      dataset.map((d) => ({ month: new Date(d.date).getMonth() })),
      (d) => d.month
    )
    .map((d) => ({ month: d[0], monthName: monthNames[d[0]], numberOfIncidents: d[1].length }))

  const currentMonth = currentDate.getMonth()
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

export function groupByGeo(dataset) {
  // Pick cities from dataset with coordinates
  const cities = dataset.map((d) => ({
    latitude: d.latitude,
    longitude: d.longitude,
    name: d.city,
    state: d.state !== undefined ? d.state : 'Abroad',
  }))

  // Group dataset by city and coordinates (some cities have the same name)
  // Reorganize the array as: [{latitude: .., longitude: .., name: .., numberOfIncidents: ..}, {..}, ...]
  // Sort the array to plot first the cities with the higher number of incidents
  const incidentsGroupedByCity = d3
    .flatRollup(
      cities,
      (v) => v.length,
      (d) => d.name,
      (d) => d.state,
      (d) => d.latitude,
      (d) => d.longitude
    )
    .map(([name, state, latitude, longitude, numberOfIncidents]) => ({
      name,
      state,
      latitude,
      longitude,
      numberOfIncidents,
    }))
    .sort((a, b) => b.numberOfIncidents - a.numberOfIncidents)

  // Remove rows without coordinates
  const incidentsGroupedFiltered = incidentsGroupedByCity.filter(
    (d) => d.latitude !== 'None' || d.longitude !== 'None'
  )

  if (incidentsGroupedByCity.length !== incidentsGroupedFiltered.length) {
    const citiesMissing = incidentsGroupedByCity - incidentsGroupedFiltered
    console.debug(`There are ${citiesMissing} cities without coordinates`)
  }

  return incidentsGroupedFiltered
}

export function countIncidentsOutsideUS(dataset) {
  return dataset.filter((d) => d.state === null).length
}

export const categoriesColors = {
  'Physical Attack': '#E07A5F',
  'Arrest/Criminal Charge': '#669599',
  'Equipment Damage': '#B0829D',
  'Equipment Search or Seizure': '#63729A',
  'Chilling Statement': '#F4C280',
  'Denial of Access': '#7EBBC8',
  'Leak Case': '#F9B29F',
  'Prior Restraint': '#98C9CD',
  'Subpoena/Legal Order': '#E2B6D0',
  'Other Incident': '#B2B8E5',
  'Border Stop': '#FBE0BC',
}
