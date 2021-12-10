import * as d3 from 'd3'
import React, { useState } from 'react'
import { countBy } from 'lodash'

function firstDayOfMonth(date) {
  const d = new Date(date)
  d.setDate(1)
  return d
}

const margins = {
  top: 1,
  left: 5,
  right: 20,
  bottom: 1,
}

export function BarChartFilter({ data, width, height }) {
  const [startDate, setStartDate] = useState('2020-01-01')
  const [endDate, setEndDate] = useState('2020-11-01')
  const frequencies = countBy(data, (d) => {
    return firstDayOfMonth(d.date).toISOString()
  })

  const definitiveData = Object.keys(frequencies).map((dateISO) => {
    return {
      date: dateISO,
      count: frequencies[dateISO],
      isSelected:
        new Date(dateISO) >= new Date(startDate + 'T00:00:00.000Z') &&
        new Date(dateISO) <= new Date(endDate + 'T00:00:00.000Z'),
    }
  })

  // console.log(
  //   'RANGE',
  //   d3.utcMonth
  //     .range(
  //       new Date(d3.min(Object.keys(frequencies))),
  //       new Date(d3.max(Object.keys(frequencies))),
  //       1
  //     )
  //     .map((monthDate) => frequencies[monthDate.toISOString()] ?? 0)
  // )
  const dateBoundaries = d3.extent(definitiveData.map((d) => new Date(d.date)))

  const xScale = d3
    .scaleTime()
    .domain(dateBoundaries)
    .range([0 + margins.left, width - margins.right])

  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(definitiveData.map((d) => d.count))])
    .range([0, height - margins.bottom - margins.top])

  return (
    <div style={{ flexDirection: 'row', maxWidth: 400 }}>
      <svg width={width} height={height} key={'BarChartWeeks'}>
        {yScale.ticks(3).map((tick, i) => (
          <g key={i + 'axes'}>
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
        {definitiveData.map((d, i) => {
          return (
            <rect
              x={xScale(new Date(d.date))}
              y={height - margins.bottom - yScale(d.count)}
              width={(width - margins.right) / 100}
              height={yScale(d.count)}
              fill={d.isSelected ? '#F2FC67' : 'black'}
              stroke={'black'}
              key={i}
              onClick={() => console.log(d.date)}
            />
          )
        })}
      </svg>
      <input
        type={'date'}
        id={'start'}
        name={'date-start'}
        value={startDate}
        min={dateBoundaries[0].toISOString().slice(0, 10)}
        max={dateBoundaries[1].toISOString().slice(0, 10)}
        onChange={() => setStartDate(document.getElementById('start').value)}
      />
      <input
        type={'date'}
        id={'end'}
        name={'trip-start'}
        value={endDate}
        min={dateBoundaries[0].toISOString().slice(0, 10)}
        max={dateBoundaries[1].toISOString().slice(0, 10)}
        onChange={() => setEndDate(document.getElementById('end').value)}
      />
    </div>
  )
}
