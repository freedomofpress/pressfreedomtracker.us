import React, { useState } from "react";
import * as d3 from "d3";
import { groupBy, countBy } from "lodash";

const margins = {
	top: 10,
	left: 5,
	right: 30,
	bottom: 50,
};

export function BarChartCategories({ data, width, height }) {
	const [hoveredElement, setHoveredElement] = useState(null);
	const years = [2017, 2018, 2019, 2020, 2021];
	const [checked, setChecked] = useState(false);
	const handleChange = () => {
		setChecked(!checked);
	};

	const incidents = data
		.map((d) => ({
			...d,
			categories: (d.categories || "").split(",").map((c) => c.trim()),
		}))
		.flatMap(({ categories, ...d }) =>
			categories.map((category) => ({ ...d, category }))
		);

	const catFrequencies = countBy(incidents, (d) => {
		return d.category;
	});

	const countCategories = Object.keys(catFrequencies).reduce(
		(acc, curr) => [
			...acc,
			{
				category: curr,
				count: catFrequencies[curr],
			},
		],
		[]
	);

	const categories = countCategories.map((d) => d.category).sort();

	const xScale = d3
		.scaleBand()
		.domain(countCategories.map((d) => d.category).sort())
		.range([0 + margins.left, width - margins.right]);

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(countCategories.map((d) => d.count))])
		.range([0, height - margins.bottom - margins.top]);

	const colorScale = d3
		.scaleOrdinal()
		.domain(countCategories.map((d) => d.category).sort())
		.range([
			"#36151e",
			"#593f62",
			"#7b6d8d",
			"#8499b1",
			"#a5c4d4",
			"#f5e0b7",
			"#d6ba73",
			"#8bbf9f",
			"#dfbbb1",
			"#41d3bd",
		]);

	const barsWidth = (width - margins.right) / 20;

	return (
		<svg width={width} height={height} key={"BarChartCategories"}>
			{yScale.ticks(4).map((tick, i) => (
				<g key={i}>
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
						textAnchor={"end"}
						fontSize={12}
					>
						{tick}
					</text>
				</g>
			))}
			{countCategories.map((d, i) => {
				return (
					<g key={i + "bars"}>
						<rect
							x={xScale(d.category)}
							y={height - margins.bottom - yScale(d.count)}
							width={barsWidth}
							height={yScale(d.count)}
							fill={hoveredElement == d.category ? "#F2FC67" : "black"}
							key={i}
							onMouseOver={() => console.log(d.category)}
							onMouseEnter={() => setHoveredElement(d.category)}
							onMouseOut={() => setHoveredElement(null)}
						/>
						{/* <line
            x1={xScale(d.category) + barsWidth/2}
            x2={xScale(d.category) + barsWidth/2}
            y1={height - margins.bottom}
            y2={height}
            stroke="black"
            strokeWidth={1}
          /> */}
					</g>
				);
			})}

			{countCategories.map((d, i) => {
				return (
					<circle
						cx={xScale(d.category) + barsWidth / 2}
						cy={height - margins.bottom / 2}
						r={3}
						fill={colorScale(d.category)}
						stroke={"gray"}
						key={d.category}
					/>
				);
			})}

			{years.map((d) => {
				return (
					<label className="container" key={d}>
						{d}
						<input type="checkbox" checked={checked} onChange={handleChange} />
						<span className="checkmark"></span>
					</label>
				);
			})}

			{/* {categories.map((d, i) => {
        return (
          <g key={i}>
            <rect
              key={i}
              x={margins.left}
              y={10 + i * 40}
              width={330}
              height={40}
              fill={'white'}
              stroke={'black'}
              strokeWidth={3}
            />
            <text
              x={margins.left + 50}
              y={i * 40}
              fill={'black'}
              key={i}
              fontSize={18}
              fontFamily={'Helvetica'}
              textAnchor={'start'}
            >
              {d}
            </text>
          </g>
        )
      })} */}
		</svg>
	);
}
