import * as d3 from 'd3'
import React from 'react'
import { AnimatedDataset } from 'react-animated-dataset'

const margins = {
  top: 20,
  left: 1,
  right: 40,
  bottom: 1,
}

export function BarChartYears({ data, width, height, selectedYears, countYears }) {
  const xScale = d3
    .scaleLinear()
    .domain(d3.extent(countYears.map((d) => d.year)))
    .range([0 + margins.left, width - margins.right])

  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(countYears.map((d) => d.count))])
    .range([0, height - margins.bottom - margins.top])
    .nice()

  const barsWidth = 10

  return (
    <div style={{ flexDirection: 'row' }}>
      <svg width={width} height={height} key={'BarChartYears'}>
        {yScale.ticks(3).map((tick, i) => (
          <g key={i} style={{ fontFamily: 'Roboto Mono' }}>
            <line
              x1={margins.left}
              x2={width}
              y1={height - margins.bottom - yScale(tick)}
              y2={height - margins.bottom - yScale(tick)}
              stroke="black"
              strokeWidth={i === 0 ? 3 : 1}
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
              width={barsWidth}
              height={yScale(d.count)}
              stroke={'black'}
              strokeWidth={2}
              fill={'black'}
              key={d}
            />
          </g>
        ))}
        <AnimatedDataset
          dataset={countYears}
          tag="rect"
          attrs={{
            x: (d) => xScale(d.year),
            y: (d) =>
              selectedYears.includes(d.year) ? height - margins.bottom - yScale(d.count) : height,
            fill: (d) => '#F2FC67',
            width: barsWidth,
            stroke: 'black',
            strokeWidth: 2,
            height: (d) => (selectedYears.includes(d.year) ? yScale(d.count) : 0),
            key: (d, i) => d,
          }}
          duration={250}
          keyFn={(d) => d.category}
        />
      </svg>
    </div>
  )
}
