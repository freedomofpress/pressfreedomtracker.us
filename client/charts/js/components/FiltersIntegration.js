import React, { useState } from "react";
import * as d3 from "d3";
import { countBy, sortBy } from "lodash";
import { BarChartCategories } from "./BarChartCategories";
import { BarChartFilter } from "./BarChartFilter";

// barChart Filter functions
function firstDayOfMonth(date) {
	return d3.timeMonth.floor(new Date(date));
}

function lastDayOfMonth(date) {
	return d3.timeMonth.ceil(new Date(date));
}

function isSubset(subset, container) {
	// all elements of subset must be present in container
	return subset.every((element) => container.includes(element));
}

export function FiltersIntegration({
	width,
	height,
	dataset: dirtyCategoriesDataset,
}) {
	const dataset = dirtyCategoriesDataset.map((d) => ({
		...d,
		categories: (d.categories || "").split(",").map((c) => c.trim()),
	}));

	const [minDate, maxDate] = d3.extent(dataset.map((d) => new Date(d.date)));

	const [startDate, setStartDate] = useState(firstDayOfMonth(minDate));
	const [endDate, setEndDate] = useState(lastDayOfMonth(maxDate));
	const [selectedCategories, setSelectedCategories] = useState([]);

	const datasetFiltered = dataset
		.filter(
			(d) =>
				new Date(d.date).getTime() >= startDate.getTime() &&
				new Date(d.date).getTime() <= endDate.getTime()
		)
		.filter((d) => isSubset(selectedCategories, d.categories));

	const monthFrequenciesObj = {
		...Object.fromEntries(
			d3.timeMonth
				.range(minDate, maxDate)
				.map((date) => [date.toISOString(), 0])
		),
		...countBy(
			dataset.filter((d) => isSubset(selectedCategories, d.categories)),
			(d) => firstDayOfMonth(d.date).toISOString()
		),
	};
	const monthFrequencies = sortBy(
		Object.entries(monthFrequenciesObj).map(([dateISO, count]) => ({
			date: dateISO,
			count,
		})),
		"date"
	);

	const monthFrequenciesFilteredObj = {
		...Object.fromEntries(
			d3.timeMonth
				.range(minDate, maxDate)
				.map((date) => [date.toISOString(), 0])
		),
		...countBy(datasetFiltered, (d) => firstDayOfMonth(d.date).toISOString()),
	};
	const monthFrequenciesFiltered = sortBy(
		Object.entries(monthFrequenciesFilteredObj).map(([dateISO, count]) => ({
			date: dateISO,
			count,
		})),
		"date"
	);

	return (
		<div>
			<h3>Categories</h3>
			<div className="chartContainer">
				<BarChartCategories
					dataset={datasetFiltered}
					width={300}
					height={150}
					selectedCategories={selectedCategories}
					setSelectedCategories={setSelectedCategories}
				/>
			</div>

			<h3>Months</h3>
			<div className="chartContainer">
				<BarChartFilter
					width={300}
					height={150}
					monthFrequencies={monthFrequencies}
					monthFrequenciesFiltered={monthFrequenciesFiltered}
					startDate={startDate}
					endDate={endDate}
					onStartDateChange={setStartDate}
					onEndDateChange={setEndDate}
				/>
			</div>
		</div>
	);
}
