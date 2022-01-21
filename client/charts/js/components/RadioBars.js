import React from 'react'
import * as d3 from 'd3'
import { countBy } from 'lodash'

const margins = {
  top: 10,
  left: 50,
  right: 20,
  bottom: 50,
}

const RADIO_BOX_WIDTH = 35

export function RadioBars({ data, width, height, onChange = () => {} }) {
  const states = countBy(data, (d) => d.state)

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

  return (
    <div>
      {countStates.map(({ state, count }, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            flexDirection: 'row',
            marginTop: 12,
            marginBottom: 12,
          }}
        >
          <div
            style={{
              display: 'flex',
              flexDirection: 'reverse-row',
              width: RADIO_BOX_WIDTH,
            }}
          >
            <input
              type="radio"
              name="drone"
              checked
              onChange={() => {
                onChange(state)
              }}
              style={{ width: 24, height: 24 }}
            />
          </div>

          <div
            key={state}
            style={{
              display: 'flex',
              flexDirection: 'column',
              // backgroundColor: 'yellow',
              alignItems: 'bottom',
              justifyContent: 'flex-end',
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between',
                marginBottom: 0,
              }}
            >
              <div
                style={{
                  color: 'black',
                  fontSize: 14,
                  lineHeight: '20px',
                  fontFamily: 'sans-serif',
                }}
              >
                {state}
              </div>
              <div
                style={{
                  fontFamily: 'Roboto Mono',
                  fontSize: 12,
                  justifyContent: 'flex-end',
                }}
              >
                {count}
              </div>
            </div>

            <svg width={width - RADIO_BOX_WIDTH} height={4}>
              <rect x={0} y={0} width={xScale(count)} height={4} fill={'black'} />
            </svg>
          </div>
        </div>
      ))}
    </div>
  )
}
