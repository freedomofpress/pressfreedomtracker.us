import React, { useState } from 'react'
import { countBy } from 'lodash'
import { BarChartYears } from './BarChartYears'
import { CheckBoxesYear } from './CheckBoxesYear'

export function FilterYears({ width, height, data }) {
  const [selectedYears, setSelectedYears] = useState([])

  const years = countBy(data, (d) => {
    return new Date(d.date).getFullYear()
  })

  const countYears = Object.entries(years).map(([year, count]) => ({
    year: Number(year),
    count,
  }))

  return (
    <div style={{ flexDirection: 'row' }}>
      <BarChartYears
        data={data}
        width={300}
        height={150}
        selectedYears={selectedYears}
        setSelectedYears={setSelectedYears}
        countYears={countYears}
      />

      <CheckBoxesYear
        width={width}
        height={height}
        options={countYears}
        setSelectedYears={setSelectedYears}
        selectedYears={selectedYears}
      />
    </div>
  )
}
