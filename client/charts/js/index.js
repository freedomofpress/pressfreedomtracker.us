import React from "react";
import { createRoot } from "react-dom";
import App from "./components/App";

function renderApp() {
	const root = createRoot(document.getElementById("react-target"));
	root.render(<App />);
}

// First render
renderApp();

// Hot module reloading
if (module.hot) {
	module.hot.accept("components/App", () => {
		console.clear();
		renderApp();
	});
}
