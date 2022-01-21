import React from 'react'

export function CheckBoxesYear({ width, height, options, setSelectedYears, selectedYears }) {
  const side = 24

  return (
    <div style={{ width, display: 'flex', flexDirection: 'column' }}>
      {options.map((d, i) => (
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
                alignItems: 'center',
                // justifyContent: 'space-between',
                marginBottom: 16,
              }}
            >
              <input
                type="checkbox"
                style={{ width: side, height: side }}
                checked={selectedYears.includes(d.year)}
                onChange={() => {
                  selectedYears.includes(d.year)
                    ? setSelectedYears(selectedYears.filter((y) => y !== d.year))
                    : setSelectedYears([...selectedYears, d.year])
                }}
              />

              <div style={{ flexDirection: 'row', marginLeft: 5, fontFamily: 'sans-serif' }}>
                {d.year}
              </div>
            </div>

            <div className="checkBoxFontFamily" style={{ display: 'flex', fontSize: 12 }}>
              {d.count}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
