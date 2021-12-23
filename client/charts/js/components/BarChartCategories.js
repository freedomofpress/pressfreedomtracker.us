import React from "react";
import * as d3 from "d3";
import { countBy } from "lodash";
import strokeCircle from "./svgIcons/strokeCircle.svg";
import fillCircle from "./svgIcons/fillCircle.svg";
import rhombus from "./svgIcons/rhombus.svg";
import doubleCircle from "./svgIcons/doubleCircle.svg";
import doubleCircleFill from "./svgIcons/doubleCircleFill.svg";
import sixPointStar from "./svgIcons/sixPointStar.svg";
import compassRose from "./svgIcons/compassRose.svg";
import diamondStar from "./svgIcons/diamondStar.svg";
import superSun from "./svgIcons/superSun.svg";
import sunStar from "./svgIcons/sunStar.svg";
import flower from "./svgIcons/flower.svg";

const margins = {
	top: 15,
	left: 5,
	right: 30,
	bottom: 30,
};

const svgIcons = {
	"Physical Attack": strokeCircle,
	"Arrest/Criminal Charge": fillCircle,
	"Equipment Damage": doubleCircle,
	"Equipment Search or Seizure": doubleCircleFill,
	"Chilling Statement": sixPointStar,
	"Denial of Access": compassRose,
	"Leak Case": rhombus,
	"Prior Restraint": diamondStar,
	"Subpoena/Legal Order": sunStar,
	"Other Incident": flower,
	"Border Stop": superSun,
};

export function BarChartCategories({
	dataset,
	width,
	height,
	selectedCategories,
	onCategoryClick,
}) {
	const incidents = dataset.flatMap(({ categories, ...d }) =>
		categories.map((category) => ({ ...d, category }))
	);

	const categoryFrequencies = {
		"Physical Attack": 0,
		"Arrest/Criminal Charge": 0,
		"Equipment Damage": 0,
		"Equipment Search or Seizure": 0,
		"Chilling Statement": 0,
		"Denial of Access": 0,
		"Leak Case": 0,
		"Prior Restraint": 0,
		"Subpoena/Legal Order": 0,
		"Other Incident": 0,
		"Border Stop": 0,
		...countBy(incidents, (d) => {
			return d.category;
		}),
	};

	const countCategories = Object.keys(categoryFrequencies).reduce(
		(acc, curr) => [
			...acc,
			{
				category: curr,
				count: categoryFrequencies[curr],
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
		.range([0, height - margins.bottom - margins.top])
		.nice(3);

	const barsWidth = (width - margins.right) / 20;
	const imageWidth = 14;

	return (
		<svg width={width} height={height} key={"BarChartCategories"}>
			{yScale.ticks(3).map((tick, i) => (
				<g key={i} style={{ fontFamily: "Roboto Mono" }}>
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
					<g key={i}>
						<rect
							x={xScale(d.category)}
							y={height - margins.bottom - yScale(d.count)}
							width={barsWidth}
							height={yScale(d.count)}
							fill={
								selectedCategories.includes(d.category) ? "#F2FC67" : "black"
							}
							stroke={"black"}
							strokeWidth={2}
							key={i}
							onClick={() => onCategoryClick(d.category)}
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
							opacity={d.count === 0 ? 0.3 : 1}
							fill={"red"}
						/>
					</g>
				);
			})}
		</svg>
	);
}
