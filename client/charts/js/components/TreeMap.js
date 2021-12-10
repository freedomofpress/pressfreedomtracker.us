import React, { useState } from 'react'
import * as d3 from 'd3'

const margins = {
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
}

const paddings = {
  top: 0,
  bottom: 40,
  right: 10,
  left: 10,
}

const textPaddings = {
  left: 10,
  right: 10,
  top: 5,
}

const borderWidth = {
  hover: 7,
  normal: 5,
}

const textStyle = {
  fontFamily: 'Helvetica Neue',
  fontWeight: '500',
  fontSize: '14px',
  lineHeight: '17px',
}

const paddingRect = borderWidth.normal
const minimumHeightText = 17

function computeMinimumNumberOfIncidents(dataset, chartHeight, minimumBarHeight) {
  const totalIncidents = dataset.length

  const y = d3
    .scaleLinear()
    .domain([0, totalIncidents])
    .range([0, chartHeight - borderWidth.normal - paddings.top - paddings.bottom])

  const minimumNumberOfIncidents = d3.min(
    d3.range(totalIncidents).filter((d) => y(d) > minimumBarHeight)
  )

  return minimumNumberOfIncidents
}

function stackDatasetByCategory(dataset, minimumNumberOfIncidents) {
  const categories = dataset.map((d) => d.categories).filter((d) => d != null)

  // Any incident having multiple categories is counted once per category
  const categoriesSimplified = [].concat.apply(
    [],
    categories.map((d) => d.split(',').map((e) => e.trim()))
  )

  // [{"Physical attack": 800, "Arrest": 50, ...}]
  const incidentsGroupedByCategory = Object.fromEntries(
    d3.rollup(
      categoriesSimplified.map((d) => ({ category: d })),
      (v) => v.length,
      (d) => d.category
    )
  )

  const incidentsGroupedByCategoryAdjusted = Object.fromEntries(
    d3.rollup(
      categoriesSimplified.map((d) => ({ category: d })),
      (v) => Math.max(v.length, minimumNumberOfIncidents),
      (d) => d.category
    )
  )

  // [{category: "Physical attack", startingPoint: 0, endPoint: 800}, {category: "Arrest", startingPoint: 800, endPoint: 850}, ...]
  const stack = d3.stack().keys(Object.keys(incidentsGroupedByCategory))
  const datasetStackedByCategory = stack([incidentsGroupedByCategoryAdjusted]).map((d) => ({
    startingPoint: d[0][0],
    endPoint: d[0][1],
    numberOfIncidents: incidentsGroupedByCategory[d.key],
    category: d.key,
  }))

  return datasetStackedByCategory
}

export function TreeMap({ data: dataset, width, height, isHomePageDesktopView, minimumBarHeight }) {
  const [hoveredElement, setHoveredElement] = useState(null)

  const minimumNumberOfIncidents = computeMinimumNumberOfIncidents(
    dataset,
    height,
    minimumBarHeight
  )

  const datasetStackedByCategory = stackDatasetByCategory(dataset, minimumNumberOfIncidents)

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(datasetStackedByCategory, (d) => d.endPoint)])
    .range([height - borderWidth.normal - paddings.top, paddings.bottom])

  const colorScale = d3.scaleOrdinal([
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
  ])

  const computeBarHeight = (start, end) => {
    return Math.max(y(start) - y(end), 1)
  }

  const openSearchPage = (category) => {
    const categoriesSlugs = {
      'Arrest/Criminal Charge': 'arrest-criminal-charge',
      'Border Stop': 'border-stop',
      'Subpoena/Legal Order': 'subpoena',
      'Leak Case': 'leak-case',
      'Equipment Search or Seizure': 'equipment-search-seizure-or-damage',
      'Physical Attack': 'physical-attack',
      'Denial of Access': 'denial-access',
      'Chilling Statement': 'chilling-statement',
      'Other Incident': 'other-incident',
      'Prior Restraint': 'prior-restraint',
      'Equipment Damage': 'equipment-damage',
    }
    const searchUrl = `https://pressfreedomtracker.us/${categoriesSlugs[category]}/`
    console.log('Going to page ' + searchUrl)
  }

  return (
    <div>
      <svg
        width={width}
        height={height}
        style={{
          marginTop: margins.top,
          marginRight: margins.right,
          marginBottom: margins.bottom,
          marginLeft: margins.left,
        }}
      >
        <line
          x1={width - paddings.left}
          x2={width}
          y1={height - paddings.bottom}
          y2={height - paddings.bottom}
          style={{ stroke: 'black', strokeWidth: isHomePageDesktopView ? borderWidth.normal : 0 }}
        />
        {datasetStackedByCategory.map((d, i) => (
          <rect
            x={paddings.left}
            y={height - y(d.startingPoint)}
            width={width - (paddings.right + paddings.left)}
            height={computeBarHeight(d.startingPoint, d.endPoint)}
            key={'Rect-' + d.category}
            style={{
              fill: colorScale(i),
              stroke: 'black',
              strokeWidth: hoveredElement === d.category ? borderWidth.hover : borderWidth.normal,
              cursor: 'pointer',
            }}
            onMouseEnter={() => setHoveredElement(d.category)}
            onMouseOut={() => setHoveredElement(null)}
            onMouseUp={() => openSearchPage(d.category)}
          >
            <title>
              {d.category}: {d.numberOfIncidents} incidents
            </title>
          </rect>
        ))}
        {datasetStackedByCategory
          .filter((d) => y(d.startingPoint) - y(d.endPoint) - paddingRect > minimumHeightText)
          .map((d, i) => (
            <g key={'Text-' + d.category}>
              <text
                y={
                  height -
                  y(d.startingPoint) +
                  computeBarHeight(d.startingPoint, d.endPoint) / 2 +
                  textPaddings.top
                }
                x={paddings.left + textPaddings.left}
                textAnchor="start"
                style={{
                  fontFamily: textStyle.fontFamily,
                  fontWeight: textStyle.fontWeight,
                  fontSize: textStyle.fontSize,
                  lineHeight: textStyle.lineHeight,
                }}
              >
                {d.category}
              </text>
              <text
                y={
                  height -
                  y(d.startingPoint) +
                  computeBarHeight(d.startingPoint, d.endPoint) / 2 +
                  textPaddings.top
                }
                x={width - textPaddings.right - paddings.right}
                textAnchor="end"
                style={{
                  fontFamily: textStyle.fontFamily,
                  fontWeight: textStyle.fontWeight,
                  fontSize: textStyle.fontSize,
                  lineHeight: textStyle.lineHeight,
                }}
              >
                {d.numberOfIncidents}
              </text>
            </g>
          ))}
      </svg>
    </div>
  )
}
