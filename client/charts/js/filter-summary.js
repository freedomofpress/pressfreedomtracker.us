import React from "react";
import { createRoot } from "react-dom/client";
import FilterSummary from "./components/FilterSummary";

function renderSummary() {
	let el = document.getElementById("filter-summary");
	let root = createRoot(el);
	root.render(<FilterSummary {...(el.dataset)} />);
}

// First render
renderSummary();

// Hot module reloading
if (module.hot) {
	module.hot.accept("components/FilterSummary", () => {
		console.clear();
		renderSummary();
	});
}
