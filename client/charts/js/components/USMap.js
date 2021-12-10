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

const USStates = [
  'California (CA)',
  'Oregon (OR)',
  'New York (NY)',
  'Virginia (VA)',
  'Missouri (MO)',
  'Colorado (CO)',
  'Texas (TX)',
  'Illinois (IL)',
  'Mississippi (MS)',
  'Michigan (MI)',
  'Florida (FL)',
  'Wisconsin (WI)',
  'District of Columbia (DC)',
  'North Carolina (NC)',
  'Georgia (GA)',
  'Minnesota (MN)',
  'Idaho (ID)',
  'Washington (WA)',
  'North Dakota (ND)',
  'Arizona (AZ)',
  'New Mexico (NM)',
  'Louisiana (LA)',
  'Utah (UT)',
  'Vermont (VT)',
  'Nebraska (NE)',
  'Pennsylvania (PA)',
  'Tennessee (TN)',
  'Kentucky (KY)',
  'Rhode Island (RI)',
  'Massachusetts (MA)',
  'Maine (ME)',
  'Oklahoma (OK)',
  'Delaware (DE)',
  'Ohio (OH)',
  'Alabama (AL)',
  'Arkansas (AR)',
  'Iowa (IA)',
  'New Jersey (NJ)',
  'Nevada (NV)',
  'Maryland (MD)',
  'South Carolina (SC)',
  'Indiana (IN)',
  'Puerto Rico (PR)',
  'Hawaii (HI)',
  'Kansas (KS)',
  'Alaska (AK)',
  'Connecticut (CT)',
  'Montana (MT)',
  'New Hampshire (NH)',
  'West Virginia (WV)',
  'South Dakota (SD)',
]

function groupByGeo(dataset) {
  // Pick cities from dataset with coordinates
  const cities = dataset.map((d) => ({
    latitude: d.latitude,
    longitude: d.longitude,
    name: d.city,
    state: USStates.includes(d.state) ? '(' + d.state.split('(')[1] : 'Abroad',
  }))

  // Group dataset by city and coordinates (some cities have the same name)
  // Reorganize the array as: [{latitude: .., longitude: .., name: .., numberOfIncidents: ..}, {..}, ...]
  // Sort the array to plot first the cities with the higher number of incidents
  const incidentsGroupedByCity = d3
    .flatRollup(
      cities,
      (v) => v.length,
      (d) => d.name,
      (d) => d.state,
      (d) => d.latitude,
      (d) => d.longitude
    )
    .map(([name, state, latitude, longitude, numberOfIncidents]) => ({
      name,
      state,
      latitude,
      longitude,
      numberOfIncidents,
    }))
    .sort((a, b) => b.numberOfIncidents - a.numberOfIncidents)

  // Remove rows without coordinates
  const incidentsGroupedFiltered = incidentsGroupedByCity.filter(
    (d) => d.latitude !== 'None' || d.longitude !== 'None'
  )

  if (incidentsGroupedByCity.length !== incidentsGroupedFiltered.length) {
    const citiesMissing = incidentsGroupedByCity - incidentsGroupedFiltered
    console.debug('There are ' + citiesMissing + ' cities without coordinates')
  }

  return incidentsGroupedFiltered
}

function countIncidentsOutsideUS(dataset) {
  return dataset.filter((d) => !USStates.includes(d.state)).length
}

export function USMap({ data: dataset, width, height }) {
  const [hoveredElement, setHoveredElement] = useState(null)

  const path = d3.geoPath()
  const projection = d3.geoAlbersUsa().scale(1280).translate([480, 300])

  const datasetAggregatedByGeo = groupByGeo(dataset)

  // Scale markers size depending on the number of incidents in a city
  const markerScale = d3.scaleLinear().domain([0, 75]).range([markerSize.min, markerSize.max])

  const openSearchPage = (city) => {
    const citySlug = city.replace(' ', '%20')
    const searchUrl = `https://pressfreedomtracker.us/all-incidents/?city=${citySlug}`
    console.log('Going to page ' + searchUrl)
  }

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
        <g key={'Markers'}>
          {datasetAggregatedByGeo.map((d, i) => (
            <circle
              cx={projection({ 0: d.longitude, 1: d.latitude })[0]}
              cy={projection({ 0: d.longitude, 1: d.latitude })[1]}
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
              key={String(d.longitude) + '-' + String(d.latitude)}
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
          Incidents recorded outside of the US: {countIncidentsOutsideUS(dataset)}
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
