import React, { useState } from "react";
import * as d3 from "d3";

const margins = {
	top: 0,
	left: 0,
	right: 0,
	bottom: 0,
};

const paddings = {
	top: 0,
	bottom: 40,
	right: 10,
	left: 10,
};

const textPaddings = {
	left: 10,
	right: 10,
	top: 5,
};

const borderWidth = {
	hover: 7,
	normal: 5,
};

const textStyle = {
	fontFamily: "Helvetica Neue",
	fontWeight: "500",
	fontSize: "14px",
	lineHeight: "17px",
};

const paddingRect = borderWidth.normal;
const minimumHeightText = 17;

const colorScale = d3.scaleOrdinal([
	"#E07A5F",
	"#669599",
	"#B0829D",
	"#63729A",
	"#F4C280",
	"#7EBBC8",
	"#F9B29F",
	"#98C9CD",
	"#E2B6D0",
	"#B2B8E5",
	"#FBE0BC",
	"#BAECF7",
	"#975544",
	"#435556",
	"#6B5261",
	"#484B6B",
	"#957932",
	"#54767D",
]);

function computeMinimumNumberOfIncidents(
	dataset,
	chartHeight,
	minimumBarHeight
) {
	const totalIncidents = dataset.length;

	const y = d3
		.scaleLinear()
		.domain([0, totalIncidents])
		.range([
			0,
			chartHeight - borderWidth.normal - paddings.top - paddings.bottom,
		]);

	const minimumNumberOfIncidents = d3.min(
		d3.range(totalIncidents).filter((d) => y(d) > minimumBarHeight)
	);

	return minimumNumberOfIncidents;
}

function stackDatasetByCategory(
	dataset,
	categoryColumn,
	categoryDivider,
	minimumNumberOfIncidents
) {
	const categories = dataset
		.map((d) => d[categoryColumn])
		.filter((d) => d != null);

	// Any incident having multiple categories is counted once per category
	const categoriesSimplified = [].concat.apply(
		[],
		categories.map((d) => d.split(categoryDivider).map((e) => e.trim()))
	);

	// [{"Physical attack": 800, "Arrest": 50, ...}]
	const incidentsGroupedByCategory = Object.fromEntries(
		d3.rollup(
			categoriesSimplified.map((d) => ({ category: d })),
			(v) => v.length,
			(d) => d.category
		)
	);

	const incidentsGroupedByCategoryAdjusted = Object.fromEntries(
		d3.rollup(
			categoriesSimplified.map((d) => ({ category: d })),
			(v) => Math.max(v.length, minimumNumberOfIncidents),
			(d) => d.category
		)
	);

	// [{category: "Physical attack", startingPoint: 0, endPoint: 800}, {category: "Arrest", startingPoint: 800, endPoint: 850}, ...]
	const stack = d3.stack().keys(Object.keys(incidentsGroupedByCategory));
	const datasetStackedByCategory = stack([
		incidentsGroupedByCategoryAdjusted,
	]).map((d, i) => ({
		startingPoint: d[0][0],
		endPoint: d[0][1],
		numberOfIncidents: incidentsGroupedByCategory[d.key],
		category: d.key,
		color: colorScale(i),
	}));

	return datasetStackedByCategory;
}

export function TreeMap({
	data: dataset,
	categoryColumn,
	categoryDivider = ",",
	width,
	height,
	isHomePageDesktopView,
	minimumBarHeight,
	titleLabel,
	openSearchPage,
}) {
	const [hoveredElement, setHoveredElement] = useState(null);

	const minimumNumberOfIncidents = computeMinimumNumberOfIncidents(
		dataset,
		height,
		minimumBarHeight
	);

	const datasetStackedByCategory = stackDatasetByCategory(
		dataset,
		categoryColumn,
		categoryDivider,
		minimumNumberOfIncidents
	);

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(datasetStackedByCategory, (d) => d.endPoint)])
		.range([height - borderWidth.normal - paddings.top, paddings.bottom]);

	const computeBarHeight = (start, end) => {
		return Math.max(yScale(start) - yScale(end), 1);
	};

	return (
		<div>
			<svg
				width={width}
				height={height}
				style={{
					marginTop: margins.top,
					marginRight: margins.right,
					marginBottom: margins.bottom,
					marginLeft: margins.left,
				}}
			>
				<line
					x1={width - paddings.left}
					x2={width}
					y1={height - paddings.bottom}
					y2={height - paddings.bottom}
					style={{
						stroke: "black",
						strokeWidth: isHomePageDesktopView ? borderWidth.normal : 0,
					}}
				/>
				{datasetStackedByCategory.map((d, i) => (
					<rect
						x={paddings.left}
						y={height - yScale(d.startingPoint)}
						width={width - (paddings.right + paddings.left)}
						height={computeBarHeight(d.startingPoint, d.endPoint)}
						key={d.category}
						style={{
							fill:
								hoveredElement === d.category || hoveredElement === null
									? d.color
									: "white",
							stroke: hoveredElement === d.category ? d.color : "black",
							strokeWidth: borderWidth.normal,
							cursor: "pointer",
						}}
						onMouseEnter={() => setHoveredElement(d.category)}
						onMouseOut={() => setHoveredElement(null)}
						onMouseUp={() => openSearchPage(d.category)}
					>
						<title>
							{d.category}: {d.numberOfIncidents} {titleLabel}
						</title>
					</rect>
				))}
				{datasetStackedByCategory.map((d, i) => (
					<line
						x1={paddings.left - borderWidth.normal / 2}
						x2={width - paddings.right + borderWidth.normal / 2}
						y1={
							height -
							yScale(d.startingPoint) +
							computeBarHeight(d.startingPoint, d.endPoint)
						}
						y2={
							height -
							yScale(d.startingPoint) +
							computeBarHeight(d.startingPoint, d.endPoint)
						}
						key={d.category}
						style={{
							stroke:
								hoveredElement === d.category
									? d.color
									: i < datasetStackedByCategory.length - 1 &&
									  hoveredElement === datasetStackedByCategory[i + 1].category
									? datasetStackedByCategory[i + 1].color
									: "black",
							strokeWidth: borderWidth.normal + 1,
							pointerEvents: "none",
						}}
					/>
				))}
				{datasetStackedByCategory
					.filter(
						(d) =>
							yScale(d.startingPoint) - yScale(d.endPoint) - paddingRect >
							minimumHeightText
					)
					.map((d, i) => (
						<g key={d.category}>
							<text
								y={
									height -
									yScale(d.startingPoint) +
									computeBarHeight(d.startingPoint, d.endPoint) / 2 +
									textPaddings.top
								}
								x={paddings.left + textPaddings.left}
								textAnchor="start"
								style={{
									fontFamily: textStyle.fontFamily,
									fontWeight: textStyle.fontWeight,
									fontSize: textStyle.fontSize,
									lineHeight: textStyle.lineHeight,
									pointerEvents: "none",
								}}
							>
								{d.category}
							</text>
							<text
								y={
									height -
									yScale(d.startingPoint) +
									computeBarHeight(d.startingPoint, d.endPoint) / 2 +
									textPaddings.top
								}
								x={width - textPaddings.right - paddings.right}
								textAnchor="end"
								style={{
									fontFamily: textStyle.fontFamily,
									fontWeight: textStyle.fontWeight,
									fontSize: textStyle.fontSize,
									lineHeight: textStyle.lineHeight,
									pointerEvents: "none",
								}}
							>
								{d.numberOfIncidents}
							</text>
						</g>
					))}
			</svg>
		</div>
	);
}
