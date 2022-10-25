import React, { useState, useEffect } from "react";
import * as d3 from "d3";
import FiltersIntegration from "./FiltersIntegration";
import { decode } from "../lib/queryString";
import "../../sass/base.sass";

export default function FilterSidebar({ serializedFilters}) {
	const [dataset, setDataset] = useState(null);
	let filters = JSON.parse(serializedFilters)

	useEffect(() => {
		const fetchPromise = fetch(`/api/edge/incidents/homepage_csv/`).then((r) => r.text())
		setDataset(null);
		fetchPromise
			.then((str) => d3.csvParse(str, d3.autoType))
			.then((json) => {
				setDataset(json);
			})
			.catch((err) => {
				console.error(err);
				return [];
			});
	}, []);

	if (dataset === null) {
		return (
			<div>
				<div
					style={{
						height: "100vh",
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
						opacity: 0.4,
						fontFamily: 'var(--font-base)',
					}}
				>
					<div>LOADING...</div>
				</div>
			</div>
		);
	}

	const urlParams = new Proxy(new URLSearchParams(window.location.search), {
		get: (searchParams, prop) => searchParams.get(prop),
	})

	let initialFilterParams = decode(urlParams)

	return (
		<FiltersIntegration
			dataset={dataset}
			width={272}
			initialFilterParams={initialFilterParams}
			filters={filters}
		/>
	);
}
