import React, { useState } from 'react'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import { AnimatedDataset } from 'react-animated-dataset'
import us from '../data/us-states.json'
import { Tooltip } from './Tooltip.js'

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

export function USMap({
  data: dataset,
  incidentsOutsideUS,
  width,
  height,
  openSearchPage,
  wrapper,
}) {
  const [hoveredElement, setHoveredElement] = useState(null)
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })

  const updateTooltipPosition = (MouseEvent) => {
    setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
  }

  const path = d3.geoPath()
  const projection = d3.geoAlbersUsa().scale(1280).translate([480, 300])
  const hasLatLon = ({ latitude, longitude }) => latitude && longitude

  // Scale markers size depending on the number of incidents in a city
  const markerScale = d3.scaleLinear().domain([0, 75]).range([markerSize.min, markerSize.max])

  return (
    <>
      {hoveredElement && hoveredElement !== 'Abroad' && (
        <Tooltip
          wrapper={wrapper.current}
          content={
            <div style={{ fontFamily: 'sans-serif', fontSize: 12, fontWeight: 500 }}>
              <div>Number of Incidents</div>
              <div
                style={{ display: 'flex', justifyContent: 'space-between', gap: 15, marginTop: 8 }}
              >
                <div style={{ borderLeft: `solid 3px #E07A5F`, paddingLeft: 3 }}>
                  {hoveredElement}
                </div>
                <div>
                  {dataset.filter((d) => `${d.name} ${d.state}` === hoveredElement).length !== 0
                    ? dataset.find((d) => `${d.name} ${d.state}` === hoveredElement)
                        .numberOfIncidents
                    : ''}
                </div>
              </div>
            </div>
          }
          x={tooltipPosition.x}
          y={tooltipPosition.y}
        />
      )}
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
              <path
                style={{ stroke: 'black', strokeWidth: mapBorder.nation }}
                d={path(d)}
                key={i}
              />
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
            <AnimatedDataset
              dataset={dataset.filter(hasLatLon)}
              tag="circle"
              init={{
                opacity: 0,
                r: 0,
                fill: (d) =>
                  hoveredElement === null
                    ? '#E07A5F'
                    : hoveredElement === `${d.name} ${d.state}`
                    ? '#E07A5F'
                    : 'white',
                strokeWidth: (d) =>
                  hoveredElement === `${d.name} ${d.state}`
                    ? markerBorder.hover
                    : markerBorder.normal,
              }}
              attrs={{
                opacity: 1,
                cx: (d) => projection([d.longitude, d.latitude])[0],
                cy: (d) => projection([d.longitude, d.latitude])[1],
                r: (d) => markerScale(d.numberOfIncidents),
                fill: (d) =>
                  hoveredElement === null
                    ? '#E07A5F'
                    : hoveredElement === `${d.name} ${d.state}`
                    ? '#E07A5F'
                    : 'white',
                stroke: 'black',
                strokeWidth: (d) =>
                  hoveredElement === `${d.name} ${d.state}`
                    ? markerBorder.hover
                    : markerBorder.normal,
              }}
              duration={250}
              keyFn={(d) => `${d.name} ${d.state}`}
            />
          </g>
          <g>
            {dataset.filter(hasLatLon).map((d) => (
              <circle
                cx={projection([d.longitude, d.latitude])[0]}
                cy={projection([d.longitude, d.latitude])[1]}
                r={markerScale(d.numberOfIncidents) + 5}
                style={{ opacity: 0, cursor: 'pointer' }}
                onMouseMove={updateTooltipPosition}
                onMouseEnter={(mouseEvent) => {
                  setHoveredElement(`${d.name} ${d.state}`)
                }}
                onMouseLeave={() => {
                  setHoveredElement(null)
                }}
                onMouseUp={(mouseEvent) => openSearchPage(d.name)}
                key={d.city + d.state}
              />
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
    </>
  )
}
