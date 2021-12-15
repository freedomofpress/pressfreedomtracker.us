import React, { useState, useEffect } from "react";
import { TreeMap } from "./TreeMap.js";
import moment from "moment";
import * as d3 from "d3";
import { BarChartFilter } from "./BarChartFilter";
import { BarChartCategories } from "./BarChartCategories";
import { RadioBars } from "./RadioBars";
import { HomepageMainCharts } from "./HomepageMainCharts.js";
import { FilterYears } from "./FilterYears.js";
import { sample } from "lodash";
import "../../sass/base.sass";

export function App() {
	const [dataset, setDataset] = useState(null);

	useEffect(() => {
		const fields = [
			// `title`,
			`categories`,
			`authors`,
			`date`,
			`city`,
			`state`,
			`latitude`,
			`longitude`,
		].join(",");

		fetch(`/api/edge/incidents/?fields=${fields}&format=csv`)
			.then((r) => r.text())
			.then((str) => d3.csvParse(str, d3.autoType))
			.then((json) => {
				// TEMPORARY - RANDOMIZE SOME COLUMNS
				json.forEach((row) => {
					row.date = row.date.toISOString();

					const cities = [
						{ name: "New York City", latitude: 40.71427, longitude: -74.00597 },
						{ name: "Albuquerque", latitude: 35.08449, longitude: -106.65114 },
						{ name: "Chicago", latitude: 41.85003, longitude: -87.65005 },
					];
					const city = sample(cities);
					row.city = city.name;
					row.latitude = city.latitude;
					row.longitude = city.longitude;
				});

				return json;
			})
			.then((json) => {
				setDataset(json);
			})
			.catch((err) => {
				console.error(err);
				return [];
			});
	}, []);

	return dataset === null ? (
		<div
			style={{
				height: "100vh",
				display: "flex",
				justifyContent: "center",
				alignItems: "center",
				opacity: 0.4,
			}}
		>
			<div>LOADING...</div>
		</div>
	) : (
		<div>
			<h1>Homepage Charts</h1>
			<div className="chartContainer">
				<HomepageMainCharts
					data={dataset}
					width={window.innerWidth - 30}
					height={window.innerWidth / 3 - 10}
					// isLastSixMonths={true}
					selectedYear={2021}
				/>
			</div>

			<h1>BarChart Categories</h1>
			<div className="chartContainer">
				<BarChartCategories data={dataset} width={300} height={150} />
			</div>

			<h1>BarChart Filter</h1>
			<div className="chartContainer">
				<BarChartFilter
					data={dataset}
					width={300}
					height={150}
					startDate={"2021-01-01"}
					endDate={"2021-11-01"}
				/>
			</div>

			<h1>BarChart Years Filter</h1>
			<div className="chartContainer">
				<FilterYears data={dataset} width={300} height={150} />
			</div>

			<h1>Radio Bars</h1>
			<div className="chartContainer">
				<RadioBars
					data={dataset}
					width={300}
					height={1600}
					startDate={"2020-01-01"}
					endDate={"2020-11-01"}
				/>
			</div>
		</div>
	);
}
