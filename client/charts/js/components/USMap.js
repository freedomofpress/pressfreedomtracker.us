import React, { useState } from 'react'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import us from '../data/us-states.json'

const margins = {
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  text: 10,
}

const paddings = {
  left: 0,
  right: 40,
  bottom: 40,
  top: 0,
  text: 5,
  map: 50,
}

const markerSize = {
  min: 5,
  max: 25,
}

const markerBorder = {
  normal: 5,
  hover: 0,
  grid: 5,
  small: 1,
}

const mapBorder = {
  states: 0.457248,
  nation: 3,
}

export function USMap({ data: dataset, incidentsOutsideUS, width, height, openSearchPage }) {
  const [hoveredElement, setHoveredElement] = useState(null)

  const path = d3.geoPath()
  const projection = d3.geoAlbersUsa().scale(1280).translate([480, 300])
  const hasLatLon = ({ latitude, longitude }) => latitude && longitude

  // Scale markers size depending on the number of incidents in a city
  const markerScale = d3.scaleLinear().domain([0, 75]).range([markerSize.min, markerSize.max])

  return (
    <svg width={width} height={height}>
      <svg
        width={width}
        height={height - (paddings.bottom + paddings.top + paddings.map)}
        style={{
          marginTop: margins.top,
          marginBottom: margins.bottom,
          marginRight: margins.right,
          marginLeft: margins.left,
        }}
        viewBox={[0, 0, 975, 610]}
      >
        <g>
          {topojson.feature(us, us.objects.nation).features.map((d, i) => (
            <path style={{ stroke: 'black', strokeWidth: mapBorder.nation }} d={path(d)} key={i} />
          ))}
        </g>
        <g style={{ fill: '#ccc' }}>
          {topojson.feature(us, us.objects.states).features.map((d, i) => (
            <path
              style={{ fill: 'white', stroke: 'black', strokeWidth: mapBorder.states }}
              d={path(d)}
              key={i}
            />
          ))}
        </g>
        <g>
          {dataset.filter(hasLatLon).map((d, i) => (
            <circle
              key={`${String(d.longitude)}-${String(d.latitude)}`}
              cx={projection([d.longitude, d.latitude])[0]}
              cy={projection([d.longitude, d.latitude])[1]}
              r={markerScale(d.numberOfIncidents)}
              style={{
                fill:
                  hoveredElement === null
                    ? '#E07A5F'
                    : hoveredElement === `${d.name} ${d.state}`
                    ? '#E07A5F'
                    : 'white',
                stroke: 'black',
                strokeWidth:
                  hoveredElement === `${d.name} ${d.state}`
                    ? markerBorder.hover
                    : markerBorder.normal,
                cursor: 'pointer',
              }}
              onMouseEnter={() => setHoveredElement(`${d.name} ${d.state}`)}
              onMouseOut={() => setHoveredElement(null)}
              onMouseUp={() => openSearchPage(d.name)}
            >
              <title>
                {d.name} {d.state}: {d.numberOfIncidents} incidents
              </title>
            </circle>
          ))}
        </g>
      </svg>
      <g>
        <line
          x1={0}
          x2={width}
          y1={height - paddings.bottom - margins.text}
          y2={height - paddings.bottom - margins.text}
          style={{ stroke: 'black', strokeWidth: markerBorder.small }}
        />
        <text
          x={paddings.text}
          y={height - paddings.bottom - margins.text - paddings.text}
          style={{
            fontSize: width > 400 ? '14px' : '12px',
            fontFamily: 'sans-serif',
            cursor: 'pointer',
            fill: hoveredElement === 'Abroad' ? '#bdbdbd' : 'black',
          }}
          onMouseEnter={() => setHoveredElement('Abroad')}
          onMouseOut={() => setHoveredElement(null)}
        >
          Incidents recorded outside of the US: {incidentsOutsideUS}
        </text>
        <text
          x={width - paddings.text}
          y={height - paddings.bottom - margins.text - paddings.text - 1}
          style={{
            fontSize: width > 400 ? '13px' : '11px',
            fontFamily: 'sans-serif',
            cursor: 'pointer',
            fill: hoveredElement === 'Abroad' ? '#bdbdbd' : '#8F8F8F',
            textAnchor: 'end',
          }}
          onMouseEnter={() => setHoveredElement('Abroad')}
          onMouseOut={() => setHoveredElement(null)}
        >
          Go to incidents &#8594;
        </text>
        <line
          x1={0}
          x2={width}
          y1={height - paddings.bottom - margins.text - paddings.text * 2 - 14}
          y2={height - paddings.bottom - margins.text - paddings.text * 2 - 14}
          style={{ stroke: 'black', strokeWidth: markerBorder.small }}
        />
      </g>
      <line
        x1={0}
        x2={width}
        y1={height - paddings.bottom}
        y2={height - paddings.bottom}
        style={{ stroke: 'black', strokeWidth: markerBorder.grid }}
      />
    </svg>
  )
}
