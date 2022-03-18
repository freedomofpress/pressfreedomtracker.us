import React, { useState, useEffect } from "react";
import * as d3 from "d3";
import { sample } from "lodash";
import HomepageMainCharts from "./HomepageMainCharts";
import FiltersIntegration from "./FiltersIntegration";
import "../../sass/base.sass";

export default function App() {
	const [dataset, setDataset] = useState(null);
	const [source, useSource] = useState("api");

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
			`tags`,
		].join(",");

		const fetchPromise =
			source === "api"
				? fetch(`/api/edge/incidents/?fields=${fields}&format=csv`).then((r) =>
						r.text()
				  )
				: import("../data/incidents.csv.js").then(({ csv }) => csv);

		setDataset(null);
		fetchPromise
			.then((str) => d3.csvParse(str, d3.autoType))
			.then((json) => {
				// TEMPORARY - RANDOMIZE SOME COLUMNS
				json.forEach((row) => {
					// This was automatically converted by d3, but subsequent code starts from stringified ISO dates
					row.date = row.date.toISOString();

					// The geo coordinates are null only in the randomized dataset, so we manually randomize them here
					const cities = [
						{ name: "New York City", latitude: 40.71427, longitude: -74.00597 },
						{ name: "Albuquerque", latitude: 35.08449, longitude: -106.65114 },
						{ name: "Chicago", latitude: 41.85003, longitude: -87.65005 },
					];
					const city = sample(cities);
					row.city = city.name;
					row.latitude = city.latitude;
					row.longitude = city.longitude;

					// These categories are wrong only in the randomized dataset but not in the production one,
					// so we manually correct them
					row.categories = row.categories
						.replace("Arrest / Criminal Charge", "Arrest/Criminal Charge")
						.replace("Subpoena / Legal Order", "Subpoena/Legal Order");
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
	}, [source]);

	const datasetButtons = (
		<>
			<button
				style={{
					backgroundColor: source === "api" ? "steelblue" : "lightgrey",
					border: "none",
					borderRadius: 5,
					padding: ".7em",
					margin: 3,
				}}
				onClick={() => useSource("api")}
			>
				live api
			</button>
			<button
				style={{
					backgroundColor: source === "static_prod" ? "steelblue" : "lightgrey",
					border: "none",
					borderRadius: 5,
					padding: ".7em",
					margin: 3,
				}}
				onClick={() => useSource("static_prod")}
			>
				static prod dataset
			</button>
		</>
	);

	if (dataset === null) {
		return (
			<div>
				{datasetButtons}
				<div
					style={{
						height: "100vh",
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
						opacity: 0.4,
						fontFamily: "sans-serif",
					}}
				>
					<div>LOADING...</div>
				</div>
			</div>
		);
	}

	return (
		<div>
			{datasetButtons}

			<h1>Homepage Charts</h1>
			<div className="chartContainer" style={{ width: "90%" }}>
				<HomepageMainCharts data={dataset} />
			</div>

			<h1>Filters Integration</h1>
			<div className="chartContainer">
				<FiltersIntegration dataset={dataset} width={300} />
			</div>
		</div>
	);
}
