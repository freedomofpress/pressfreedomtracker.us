import React from "react";
import ReactDOM from "react-dom";
import FilterSidebar from "./components/FilterSidebar";

function renderSidebar() {
	let el = document.getElementById("filter-sidebar");
	ReactDOM.render(<FilterSidebar {...(el.dataset)} />, el);
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
