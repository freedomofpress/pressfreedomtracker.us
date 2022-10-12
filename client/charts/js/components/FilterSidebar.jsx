import React, { useState, useEffect } from "react";
import * as d3 from "d3";
import FiltersIntegration from "./FiltersIntegration";
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


	let activeCategories, categoryParameters = new Set(), initialFilterParams = {}
	if (!urlParams.categories || urlParams.categories.length === 0) {
		activeCategories = new Set()
	} else {
		activeCategories = new Set(urlParams.categories.split(",").map(Number))
	}
	for (const category of filters) {
		// if (category.id === -1) { continue }  // non-categorized filters have an id of -1
		if (activeCategories.has(category.id)) {
			categoryParameters.add(category.title)
		}
		for (const filter of category.filters) {
			if (filter.type === 'date') {
				let lowerValue = urlParams[`${filter.name}_lower`]
				let upperValue = urlParams[`${filter.name}_upper`]
				initialFilterParams[filter.name] = {
					enabled: false,
					type: filter.type,
					parameters: {
						min: lowerValue ? new Date(lowerValue) : null,
						max: upperValue ? new Date(upperValue) : null,
					},
				}
			} else {
				initialFilterParams[filter.name] = {
					enabled: false,
					type: filter.type,
					parameters: urlParams[filter.name]
				}
			}
		}
	}
	initialFilterParams.filterCategory = { type: 'category', parameters: categoryParameters, enabled: true }

	return (
		<FiltersIntegration
			dataset={dataset}
			width={272}
			initialFilterParams={initialFilterParams}
			filters={filters}
		/>
	);
}
