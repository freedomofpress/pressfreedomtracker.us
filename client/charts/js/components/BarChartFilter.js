import * as d3 from "d3";
import React from "react";
import { sortBy } from "lodash";

const margins = {
	top: 15,
	left: 5,
	right: 30,
	bottom: 3,
};

function isDateValid(date) {
	return !Number.isNaN(new Date(date).getYear());
}

function monthWidth(date, scale) {
	return scale(d3.timeMonth.offset(new Date(date), 1)) - scale(new Date(date));
}

function closeLineArea(dataset) {
	const [dateMax, dateMin] = d3.extent(dataset.map((d) => d.date));
	return [
		{
			date: d3.timeMonth.offset(new Date(dateMin), 1).toISOString(),
			count: 0,
		},
		...dataset,
		{
			date: dateMax,
			count: 0,
		},
	];
}

export function BarChartFilter({
	width,
	height,
	monthFrequencies,
	monthFrequenciesFiltered,
	startDate,
	endDate,
	onStartDateChange,
	onEndDateChange,
}) {
	const dateBoundaries = d3.extent(
		monthFrequencies.map((d) => new Date(d.date))
	);

	const xScale = d3
		.scaleTime()
		.domain(dateBoundaries)
		.range([0 + margins.left, width - margins.right]);

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(monthFrequencies.map((d) => d.count))])
		.range([0 + margins.top, height - margins.bottom - margins.top])
		.nice(3);

	const yScaleLine = yScale
		.copy()
		.range([height - margins.bottom - margins.top, 0 + margins.top]);

	const lineGenerator = d3
		.line()
		.curve(d3.curveStepAfter)
		.x((d) => xScale(new Date(d.date)))
		.y((d) => yScaleLine(d.count));

	return (
		<div style={{ flexDirection: "row" }}>
			<svg width={width} height={height}>
				{yScale.ticks(3).map((tick, i) => (
					<g key={i} style={{ fontFamily: "Roboto Mono" }}>
						<line
							x1={margins.left}
							x2={width}
							y1={height - margins.bottom - yScale(tick) + (i === 0 ? 1.5 : 0)}
							y2={height - margins.bottom - yScale(tick) + (i === 0 ? 1.5 : 0)}
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

				{monthFrequencies.map((d, i) => {
					return (
						<rect
							key={i}
							x={xScale(new Date(d.date))}
							y={height - margins.bottom - yScale(d.count)}
							width={monthWidth(d.date, xScale) + 0.5}
							height={yScale(d.count) - margins.top}
							fill={"black"}
						/>
					);
				})}

				{monthFrequenciesFiltered.map((d, i) => {
					return (
						<rect
							key={i}
							x={xScale(new Date(d.date))}
							y={height - margins.bottom - yScale(d.count)}
							width={monthWidth(d.date, xScale) + 0.5}
							height={yScale(d.count) - margins.top}
							fill={"#F2FC67"}
						/>
					);
				})}

				<path
					d={lineGenerator(
						sortBy(closeLineArea(monthFrequenciesFiltered), (d) => d.date)
					)}
					stroke={"black"}
					strokeWidth={1}
					fill={"none"}
				/>
			</svg>

			<div
				style={{
					display: "flex",
					width: "100%",
					justifyContent: "space-between",
				}}
			>
				<input
					type={"date"}
					value={startDate.toISOString().slice(0, 10)}
					min={dateBoundaries[0].toISOString().slice(0, 10)}
					max={dateBoundaries[1].toISOString().slice(0, 10)}
					onChange={(event) => {
						if (isDateValid(event.target.value))
							onStartDateChange(new Date(event.target.value));
					}}
					style={{ flexBasis: "50%" }}
				/>
				<input
					type={"date"}
					value={endDate.toISOString().slice(0, 10)}
					min={dateBoundaries[0].toISOString().slice(0, 10)}
					max={dateBoundaries[1].toISOString().slice(0, 10)}
					onChange={(event) => {
						if (isDateValid(event.target.value))
							onEndDateChange(new Date(event.target.value));
					}}
					style={{ flexBasis: "50%" }}
				/>
			</div>
		</div>
	);
}
