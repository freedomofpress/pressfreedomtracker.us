import React, { useState } from 'react'

export function CheckBoxesYear({ width, height, options, setSelectedYears, selectedYears }) {
  const side = 24
  const spaceBetweenRects = 4
  return (
    <div style={{ width, display: 'flex', flexDirection: 'column' }}>
      {options
        //.sort((a, b) => b - a)
        .map((d, i) => (
          <div key={d.year}>
            <div
              style={{
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'row',
                  fontSize: 14,
                  //alignItems: 'center',
                  //justifyContent: 'space-between',
                  marginBottom: 16,
                }}
              >
                <svg width={side} height={side}>
                  <rect
                    x={1}
                    y={1}
                    width={side - 2}
                    height={side - 2}
                    key={i + 'box'}
                    stroke={'black'}
                    fill={selectedYears.includes(d.year) ? 'black' : 'white'}
                    onClick={() => {
                      selectedYears.includes(d.year)
                        ? setSelectedYears(selectedYears.filter((y) => y != d.year))
                        : setSelectedYears([...selectedYears, d.year])
                    }}
                  />
                </svg>

                <div style={{ flexDirection: 'row' }}>{d.year}</div>
              </div>

              <div style={{ display: 'flex' }}>{d.count}</div>
            </div>
          </div>
        ))}
    </div>
  )
}
