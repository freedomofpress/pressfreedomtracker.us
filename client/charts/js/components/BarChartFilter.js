import * as d3 from "d3";
import React, { useState } from "react";
import { countBy } from "lodash";

function firstDayOfMonth(date) {
	return d3.timeMonth.floor(new Date(date));
}

function lastDayOfMonth(date) {
	return d3.timeMonth.ceil(new Date(date));
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

function monthWidth(date, scale) {
	return scale(d3.timeMonth.offset(new Date(date), 1)) - scale(new Date(date));
}

const margins = {
	top: 0,
	left: 5,
	right: 30,
	bottom: 3,
};

export function BarChartFilter({ data, width, height }) {
	const [minDate, maxDate] = d3.extent(data.map((d) => new Date(d.date)));

	const [startDate, setStartDate] = useState(firstDayOfMonth(minDate));
	const [endDate, setEndDate] = useState(lastDayOfMonth(maxDate));

	const frequencies = countBy(data, (d) =>
		firstDayOfMonth(d.date).toISOString()
	);

	const totalDataGrouped = Object.keys(frequencies).map((dateISO) => {
		return {
			date: dateISO,
			count: frequencies[dateISO],
			isSelected:
				new Date(dateISO) >= startDate && new Date(dateISO) <= endDate,
		};
	});

	const dataFiltered = data.filter(
		(d) =>
			new Date(d.date).getTime() >= startDate.getTime() &&
			new Date(d.date).getTime() <= endDate.getTime()
	);

	const countDataFiltered = countBy(dataFiltered, (d) =>
		firstDayOfMonth(d.date).toISOString()
	);

	const filteredDataGrouped = Object.keys(countDataFiltered).map((dateISO) => {
		return {
			date: dateISO,
			count: countDataFiltered[dateISO],
		};
	});

	const dateBoundaries = d3.extent(
		totalDataGrouped.map((d) => new Date(d.date))
	);

	const xScale = d3
		.scaleTime()
		.domain(dateBoundaries)
		.range([0 + margins.left, width - margins.right]);

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(totalDataGrouped.map((d) => d.count))])
		.range([0, height - margins.bottom]);
	// .nice(3)

	const yScaleLine = yScale.copy().range([height - margins.bottom, 0]);

	const lineGenerator = d3
		.line()
		.curve(d3.curveStepBefore)
		.x((d) => xScale(new Date(d.date)))
		.y((d) => yScaleLine(d.count));

	return (
		<div style={{ flexDirection: "row" }}>
			<svg width={width} height={height} key={"BarChartWeeks"}>
				{yScale.ticks(3).map((tick, i) => (
					<g key={i} className="axesFontFamily">
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

				{totalDataGrouped.map((d, i) => {
					return (
						<rect
							x={xScale(new Date(d.date))}
							y={height - margins.bottom - yScale(d.count)}
							width={monthWidth(d.date, xScale) + 0.5}
							height={yScale(d.count)}
							fill={"black"}
							key={i}
						/>
					);
				})}

				{filteredDataGrouped.map((d, i) => {
					return (
						<rect
							x={xScale(new Date(d.date))}
							y={height - margins.bottom - yScale(d.count)}
							width={monthWidth(d.date, xScale) + 0.5}
							height={yScale(d.count)}
							fill={"#F2FC67"}
							key={i}
						/>
					);
				})}

				<path
					d={lineGenerator(closeLineArea(filteredDataGrouped))}
					stroke={"black"}
					strokeWidth={1}
					fill={"none"}
				/>
			</svg>

			<div>
				<input
					type={"date"}
					name={"date-start"}
					value={startDate.toISOString().slice(0, 10)}
					min={dateBoundaries[0].toISOString().slice(0, 10)}
					max={dateBoundaries[1].toISOString().slice(0, 10)}
					onChange={(event) => {
						const d = new Date(event.target.value);
						if (!Number.isNaN(d.getYear())) setStartDate(d);
					}}
					style={{ width: "50%" }}
				/>
				<input
					type={"date"}
					name={"trip-start"}
					value={endDate.toISOString().slice(0, 10)}
					min={dateBoundaries[0].toISOString().slice(0, 10)}
					max={dateBoundaries[1].toISOString().slice(0, 10)}
					onChange={(event) => {
						const d = new Date(event.target.value);
						if (!Number.isNaN(d.getYear())) setEndDate(d);
					}}
					style={{ width: "50%" }}
				/>
			</div>
		</div>
	);
}
