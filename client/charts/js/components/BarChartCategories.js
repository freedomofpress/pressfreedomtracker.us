import React, { useState } from "react";
import * as d3 from "d3";
import { countBy } from "lodash";
import strokeCircle from "./svgIcons/Ellipse 238.svg";
import fillCircle from "./svgIcons/Ellipse 239.svg";
import rhombus from "./svgIcons/Exclude.svg";
import doubleCircle from "./svgIcons/Group 35.svg";
import doubleCircleFill from "./svgIcons/Group 36.svg";
import sixPointStar from "./svgIcons/Star 1_new.svg";
import compassRose from "./svgIcons/Star 2.svg";
import diamondStar from "./svgIcons/Star 3.svg";
import superSun from "./svgIcons/star4.svg";
import sunStar from "./svgIcons/Star 5.svg";
import flower from "./svgIcons/Vector.svg";

const margins = {
	top: 10,
	left: 5,
	right: 30,
	bottom: 30,
};

const svgIcons = {
	"Physical Attack": strokeCircle,
	"Arrest/Criminal Charge": fillCircle,
	"Arrest / Criminal Charge": fillCircle, // redundant to catch both
	"Equipment Damage": doubleCircle,
	"Equipment Search or Seizure": doubleCircleFill,
	"Chilling Statement": sixPointStar,
	"Denial of Access": compassRose,
	"Leak Case": rhombus,
	"Prior Restraint": diamondStar,
	"Subpoena/Legal Order": sunStar,
	"Subpoena / Legal Order": sunStar, // redundant to catch both
	"Other Incident": flower,
	"Border Stop": superSun,
};

export function BarChartCategories({ data, width, height }) {
	const [hoveredElement, setHoveredElement] = useState(null);

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

	const xScale = d3
		.scaleBand()
		.domain(countCategories.map((d) => d.category).sort())
		.range([0 + margins.left, width - margins.right]);

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(countCategories.map((d) => d.count))])
		.range([0, height - margins.bottom - margins.top]);

	const barsWidth = (width - margins.right) / 20;
	const imageWidth = 14;

	return (
		<svg width={width} height={height} key={"BarChartCategories"}>
			{yScale.ticks(4).map((tick, i) => (
				<g key={i} className="axesFontFamily">
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
						textAnchor={"end"}
						fontSize={12}
					>
						{tick}
					</text>
				</g>
			))}
			{countCategories.map((d, i) => {
				return (
					<g key={`${i} bars`}>
						<rect
							x={xScale(d.category)}
							y={height - margins.bottom - yScale(d.count)}
							width={barsWidth}
							height={yScale(d.count)}
							fill={hoveredElement === d.category ? "#F2FC67" : "black"}
							stroke={"black"}
							strokeWidth={2}
							key={i}
							onMouseOver={() => console.log(d.category)}
							onMouseEnter={() => setHoveredElement(d.category)}
							onMouseOut={() => setHoveredElement(null)}
						/>
					</g>
				);
			})}

			{countCategories.map((d, i) => {
				return (
					<g key={i}>
						<image
							width={imageWidth}
							height={imageWidth}
							x={xScale(d.category) + barsWidth / 2 - imageWidth / 2}
							y={height - margins.bottom / 2}
							href={svgIcons[d.category]}
							transform={"translate(-50% ,0)"}
						/>
					</g>
				);
			})}
		</svg>
	);
}
