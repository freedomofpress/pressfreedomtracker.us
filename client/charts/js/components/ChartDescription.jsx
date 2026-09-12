import React from "react";
import PropTypes from "prop-types";
import "../../scss/ChartDescription.scss";

export default function ChartDescription({ id, children }) {
	return (
		<div id={id} className="chartDescription">
			{children}
		</div>
	);
}

ChartDescription.propTypes = {
	id: PropTypes.string,
	children: PropTypes.node.isRequired,
};
