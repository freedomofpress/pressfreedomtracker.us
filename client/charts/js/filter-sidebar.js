import React from "react";
import { createRoot } from "react-dom/client";
import FilterSidebar from "./components/FilterSidebar";

function renderSidebar() {
	let el = document.getElementById("filter-sidebar");
	let root = createRoot(el);
	root.render(<FilterSidebar {...(el.dataset)} />);
}

// First render
renderSidebar();

// Hot module reloading
if (module.hot) {
	module.hot.accept("components/FilterSidebar", () => {
		console.clear();
		renderSidebar();
	});
}
