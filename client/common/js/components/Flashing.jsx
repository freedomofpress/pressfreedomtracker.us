import React from "react";

import "./Flashing.scss";

export default function Flashing({ flashing = true, children }) {
	return (
		<div className={flashing ? "flashing" : "flashing flashing--off"}>
			{children}
		</div>
	);
}
