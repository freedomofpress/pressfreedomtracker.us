import React, { useState } from 'react'
import * as d3 from 'd3'

const margins = {
  top: 0,
  left: 0,
  right: 2,
  bottom: 0,
}

const paddings = {
  left: 10,
  right: 10,
  bottom: 40,
  top: 40,
}

const paddingsInternal = {
  left: 10,
  right: 40,
}

const barDistances = {
  year: 5,
  semester: 10,
}

const borders = {
  normal: 5,
  hover: 7,
  grid: 1,
}

const textPadding = 10

const monthNames = [
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

const monthIndexes = {
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

const numberOfGridLines = 3

function filterByLastSixMonths(dataset, currentDate) {
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

function filterByYear(dataset, selectedYear) {
  return dataset.filter((d) => new Date(d.date).getFullYear() === selectedYear)
}

function groupByMonthSorted(dataset, isLastSixMonths, currentDate) {
  // Computes the number of incidents by month
  const datasetGroupedByMonth = d3
    .groups(
      dataset.map((d) => ({ month: new Date(d.date).getMonth() })),
      (d) => d.month
    )
    .map((d) => ({ month: d[0], monthName: monthNames[d[0]], numberOfIncidents: d[1].length }))

  // Indexes of the last six months
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
    : datasetGroupedByMonth.sort((a, b) => a.month - b.month)

  return datasetGroupedByMonthSorted
}

/*
    - "isLastSixMonths" is true whether the data refers to the last six months
*/
export function BarChartHomepage({
  data: dataset,
  isLastSixMonths,
  selectedYear,
  currentDate = new Date(),
  width,
  height,
}) {
  const [hoveredElement, setHoveredElement] = useState(null)

  const datasetFilteredByPeriod = isLastSixMonths
    ? filterByLastSixMonths(dataset, currentDate)
    : filterByYear(dataset, selectedYear)
  const datasetGroupedByMonth = groupByMonthSorted(
    datasetFilteredByPeriod,
    isLastSixMonths,
    currentDate
  )

  const numberOfBars = isLastSixMonths ? 6 : 12
  const barDistance = isLastSixMonths ? barDistances.semester : barDistances.year
  const chartWidth =
    width - paddings.left - paddings.right - paddingsInternal.left - paddingsInternal.right
  const barWidth = chartWidth / numberOfBars - barDistance * 2

  // Grid lines are computed so that the last one is placed slightly above the highest bar at a round value
  const baseGridValue =
    Math.ceil(
      Math.ceil(d3.max(datasetGroupedByMonth, (d) => d.numberOfIncidents) / numberOfGridLines) / 10
    ) * 10

  const gridLines = d3.range(0, numberOfGridLines + 1).map((d) => d * baseGridValue)

  // Remapping on the y coords
  const y = d3
    .scaleLinear()
    .domain([0, baseGridValue * numberOfGridLines])
    .range([height - paddings.bottom, paddings.top])

  // Remapping on the x coords
  const x = (barIndex) => {
    return (
      (chartWidth * barIndex) / numberOfBars + paddings.left + paddingsInternal.left + barDistance
    )
  }

  const computeBarheight = (numberOfIncidents) => {
    return height - y(numberOfIncidents) - paddings.bottom
  }

  const openSearchPage = (month) => {
    const monthNumber = monthIndexes[month]
    const year = !isLastSixMonths
      ? selectedYear
      : monthNumber > 6 && currentDate.getMonth < 6
      ? currentDate.getFullYear() - 1
      : currentDate.getFullYear()
    const firstDayMonth = `${year}-${monthNumber}-1`
    const lastDayMonth = `${year}-${monthNumber}-${new Date(year, monthNumber, 0).getDate()}`
    const searchUrl = `https://pressfreedomtracker.us/all-incidents/?date_lower=${firstDayMonth}&date_upper=${lastDayMonth}`
    console.log('Going to page ' + searchUrl)
  }

  return (
    <svg
      width={width}
      height={height}
      style={{
        marginTop: margins.top,
        marginBottom: margins.bottom,
        marginRight: margins.right,
        marginLeft: margins.left,
      }}
    >
      {gridLines.map((d) => (
        <g key={'gridLine-' + String(d)}>
          <line
            x1={d === 0 ? 0 : paddings.left}
            x2={width - paddings.right}
            y1={y(d)}
            y2={y(d)}
            style={{ stroke: 'black', strokeWidth: d === 0 ? borders.normal : borders.grid }}
          />
          <text
            x={width - paddings.right}
            y={y(d) - textPadding}
            textAnchor="end"
            style={{
              fontFamily: 'monospace',
              fontSize: '12px',
            }}
          >
            {d}
          </text>
        </g>
      ))}
      {datasetGroupedByMonth.map((d, i) => (
        <g key={'Bar-' + d.monthName}>
          <rect
            x={x(i)}
            y={y(d.numberOfIncidents)}
            height={computeBarheight(d.numberOfIncidents)}
            width={barWidth}
            style={{
              fill: '#E07A5F',
              strokeWidth: hoveredElement === d.monthName ? borders.hover : borders.normal,
              stroke: 'black',
              cursor: 'pointer',
            }}
            onMouseEnter={() => setHoveredElement(d.monthName)}
            onMouseOut={() => setHoveredElement(null)}
            onMouseUp={() => openSearchPage(d.monthName)}
          >
            <title>
              {d.monthName}: {d.numberOfIncidents} incidents
            </title>
          </rect>
          <text
            x={x(i) + barWidth / 2}
            y={height - paddings.bottom / 2}
            textAnchor="middle"
            style={{
              fontFamily: 'sans-serif',
              fontWeight: 500,
              fontSize: '14px',
            }}
          >
            {d.monthName}
          </text>
        </g>
      ))}
    </svg>
  )
}
