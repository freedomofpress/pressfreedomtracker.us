import * as d3 from 'd3'
import React, { useState } from 'react'
import { groupBy, countBy } from 'lodash'
import { CheckBoxesYear } from './CheckBoxesYear'

const margins = {
  top: 20,
  left: 5,
  right: 40,
  bottom: 1,
}

export function BarChartYears({ data, width, height }) {
  const [selectedYears, setSelectedYears] = useState([])

  const years = countBy(data, (d) => {
    return new Date(d.date).getFullYear()
  })

  const countYears = Object.entries(years).map(([year, count]) => ({
    year: Number(year),
    count,
  }))
  console.log(countYears.map((d) => d.year))

  const xScale = d3
    .scaleLinear()
    .domain(d3.extent(countYears.map((d) => d.year)))
    .range([0 + margins.left, width - margins.right])

  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(countYears.map((d) => d.count))])
    .range([0, height - margins.bottom - margins.top])

  return (
    <div style={{ flexDirection: 'row' }}>
      <svg width={width} height={height} key={'BarChartYears'}>
        {yScale.ticks(3).map((tick, i) => (
          <g key={i}>
            <line
              x1={margins.left}
              x2={width}
              y1={height - margins.bottom - yScale(tick)}
              y2={height - margins.bottom - yScale(tick)}
              stroke="black"
              strokeWidth={1}
            />
            <text
              x={width}
              y={height - margins.bottom - yScale(tick) - 4}
              textAnchor={'end'}
              fontSize={12}
            >
              {tick}
            </text>
          </g>
        ))}
        {countYears.map((d, i) => (
          <g key={i}>
            <rect
              x={xScale(d.year)}
              y={height - margins.bottom - yScale(d.count)}
              width={10}
              height={yScale(d.count)}
              stroke={'black'}
              fill={selectedYears.includes(d.year) ? '#F2FC67' : 'white'}
              key={d}
            />
          </g>
        ))}
      </svg>
      <div style={{ flexDirection: 'row' }}>
        <CheckBoxesYear
          width={width}
          height={height}
          //options={countYears.map((d) => d.year)}
          options={countYears}
          setSelectedYears={setSelectedYears}
          selectedYears={selectedYears}
        />
      </div>
    </div>
  )
}
