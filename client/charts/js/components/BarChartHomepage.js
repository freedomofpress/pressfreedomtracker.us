import React, { useState } from "react";
import * as d3 from "d3";
import { Slider } from "./Slider.js";

const margins = {
	top: 0,
	left: 0,
	right: 2,
	bottom: 0,
};

const paddings = {
	left: 10,
	right: 10,
	bottom: 40,
	top: 40,
	mobile: 80,
};

const paddingsInternal = {
	left: 10,
	right: 40,
};

const borders = {
	normal: 5,
	hover: 7,
	grid: 1,
};

const textPadding = 10;

export function BarChartHomepage({
	data: dataset,
	x,
	y,
	titleLabel,
	isMobileView,
	width,
	height,
	numberOfTicks = 4,
	openSearchPage,
}) {
	const [hoveredElement, setHoveredElement] = useState(null);
	const [sliderSelection, setSliderSelection] = useState(dataset[0][x]);

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(dataset, (d) => d[y])])
		.range([
			height - (isMobileView ? paddings.mobile : paddings.bottom),
			paddings.top,
		])
		.nice(numberOfTicks);

	const gridLines = yScale.ticks(numberOfTicks);

	const xScale = d3
		.scaleBand()
		.domain(dataset.map((d) => d[x]))
		.range([
			paddings.left + paddingsInternal.left,
			width - paddings.right - paddingsInternal.right,
		])
		.paddingInner(0.3)
		.paddingOuter(0.2);

	const xScaleOverLayer = d3
		.scaleBand()
		.domain(dataset.map((d) => d[x]))
		.range([
			paddings.left + paddingsInternal.left,
			width - paddings.right - paddingsInternal.right,
		]);

	const xSlider = d3
		.scalePoint()
		.domain(dataset.map((d) => d[x]))
		.range([0, width])
		.padding(0.3);

	const computeBarheight = (y) => {
		return (
			height - yScale(y) - (isMobileView ? paddings.mobile : paddings.bottom)
		);
	};

	const selectedElement = dataset.find((d) => d[x] === sliderSelection);
	const incidentsCount = selectedElement !== undefined ? selectedElement[y] : 0;

	if (!isMobileView) {
		return (
			<svg
				width={width}
				height={height}
				style={{
					marginTop: margins.top,
					marginBottom: margins.bottom,
					marginRight: margins.right,
					marginLeft: margins.left,
				}}
			>
				{gridLines.map((d) => (
					<g key={String(d)}>
						<line
							x1={d === 0 ? 0 : paddings.left}
							x2={width - paddings.right}
							y1={yScale(d)}
							y2={yScale(d)}
							style={{
								stroke: "black",
								strokeWidth: d === 0 ? borders.normal : borders.grid,
							}}
						/>
						<text
							x={width - paddings.right}
							y={yScale(d) - textPadding}
							textAnchor="end"
							style={{
								fontFamily: "monospace",
								fontSize: "12px",
							}}
						>
							{d}
						</text>
					</g>
				))}
				{dataset.map((d) => (
					<g key={d[x]}>
						<rect
							x={xScale(d[x])}
							y={yScale(d[y])}
							height={computeBarheight(d[y])}
							width={xScale.bandwidth()}
							style={{
								fill:
									hoveredElement === d[x]
										? "#E07A5F"
										: hoveredElement === null
										? "#E07A5F"
										: "white",
								strokeWidth: borders.normal,
								stroke: hoveredElement === d[x] ? "#E07A5F" : "black",
								cursor: "pointer",
							}}
						/>
						<rect
							x={xScaleOverLayer(d[x])}
							y={yScale(d[y])}
							height={computeBarheight(d[y])}
							width={xScaleOverLayer.bandwidth()}
							style={{
								opacity: 0,
								cursor: "pointer",
							}}
							onMouseEnter={() => setHoveredElement(d[x])}
							onMouseOut={() => setHoveredElement(null)}
							onMouseUp={() => openSearchPage(d[x])}
						>
							<title>
								{d[x]}: {d[y]} {titleLabel}
							</title>
						</rect>
						<text
							x={xScale(d[x]) + xScale.bandwidth() / 2}
							y={height - paddings.bottom / 2}
							textAnchor="middle"
							style={{
								fill: hoveredElement === d[x] ? "#E07A5F" : "black",
								fontFamily: "sans-serif",
								fontWeight: 500,
								fontSize: "14px",
							}}
						>
							{d[x]}
						</text>
					</g>
				))}
			</svg>
		);
	} else {
		return (
			<svg
				width={width}
				height={height}
				style={{
					marginTop: margins.top,
					marginBottom: margins.bottom,
					marginRight: margins.right,
					marginLeft: margins.left,
				}}
				id="barchart-svg"
			>
				{gridLines.map((d) => (
					<g key={String(d)}>
						<line
							x1={d === 0 ? 0 : paddings.left}
							x2={width - paddings.right}
							y1={yScale(d)}
							y2={yScale(d)}
							style={{
								stroke: "black",
								strokeWidth: d === 0 ? borders.normal : borders.grid,
							}}
						/>
						<text
							x={width - paddings.right}
							y={yScale(d) - textPadding}
							textAnchor="end"
							style={{
								fontFamily: "monospace",
								fontSize: "12px",
							}}
						>
							{d}
						</text>
					</g>
				))}
				{dataset.map((d) => (
					<g key={d[x]}>
						<rect
							x={xScale(d[x])}
							y={yScale(d[y])}
							height={computeBarheight(d[y])}
							width={xScale.bandwidth()}
							style={{
								fill:
									sliderSelection === d[x]
										? "#E07A5F"
										: sliderSelection === null
										? "#E07A5F"
										: "white",
								strokeWidth: borders.normal,
								stroke: sliderSelection === d[x] ? "#E07A5F" : "black",
								cursor: "pointer",
							}}
							onMouseUp={() => openSearchPage(d[x])}
						>
							<title>
								{d[x]}: {d[y]} {titleLabel}
							</title>
						</rect>
					</g>
				))}

				<Slider
					elements={dataset.map((d) => d[x])}
					xScale={xSlider}
					ycoord={height - paddings.bottom / 2}
					setSliderSelection={setSliderSelection}
					sliderSelection={sliderSelection}
					idContainer={"barchart-svg"}
				/>

				<text
					x={width / 2}
					y={height - paddings.mobile / 2 - 7}
					textAnchor="middle"
					style={{
						fill: "black",
						fontFamily: "sans-serif",
						fontWeight: 500,
						fontSize: "14px",
					}}
				>
					{`${sliderSelection} ${incidentsCount} ${titleLabel}`}
				</text>
			</svg>
		);
	}
}
