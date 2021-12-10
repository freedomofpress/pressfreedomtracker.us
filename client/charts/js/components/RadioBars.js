import React from 'react'
import * as d3 from 'd3'
import { countBy } from 'lodash'

const margins = {
  top: 10,
  left: 50,
  right: 20,
  bottom: 50,
}

export function RadioBars({ data, startDate, endDate, width, height }) {
  const states = countBy(data, (d) => {
    return d.state
  })

  const countStates = Object.entries(states)
    .map(([state, count]) => ({
      state: state,
      count: count,
    }))
    .sort((a, b) => b.count - a.count)

  const xScale = d3
    .scaleLinear()
    .domain([0, d3.max(countStates.map((d) => d.count))])
    .range([margins.left, width - margins.right])

  const yScale = d3
    .scaleBand()
    .domain(countStates.map((d) => d.state).slice(0, 3))
    .range([0 + margins.bottom, height - margins.top])
    .paddingInner(0.5)

  return (
    <div>
      {countStates.map((d, i) => (
        <div key={d.state}>
          <div style={{ color: 'black', fontSize: 14, fontFamily: 'sans-serif' }}>{d.state}</div>
          <div
            style={{
              fontSize: 12,
              fontFamily: 'sans-serif',
              // backgroundColor: '#F2F2F2',
              // width: 25,
              justifyContent: 'flex-end',
            }}
          >
            {d.count}
          </div>
          <svg width={width} height={4}>
            <rect
              x={0}
              y={0}
              width={xScale(d.count)}
              //width={width - margins.left - margins.right - xScale(d.count)}
              height={4}
              fill={'black'}
            />
          </svg>
        </div>
      ))}
    </div>
  )
}
