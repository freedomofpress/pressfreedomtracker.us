import React from "react";
import PropTypes from "prop-types";
import * as d3 from "d3";
import { countBy } from "lodash";
import RadioBar from "./RadioBar";

const margins = {
	top: 10,
	left: 50,
	right: 30,
	bottom: 50,
};

export default function StateFilter({
	dataset,
	width,
	filterParameters: selectedState,
	setFilterParameters: setSelectedState,
}) {
	const states = countBy(
		dataset.filter((d) => d.state !== null),
		(d) => d.state,
	);

	states.All = dataset.length;

	const countStates = Object.entries(states)
		.map(([state, count]) => ({
			state: state,
			count: count,
		}))
		.sort((a, b) => b.count - a.count);

	const xScale = d3
		.scaleLinear()
		.domain([0, d3.max(countStates.map((d) => d.count))])
		.range([margins.left, width - margins.right - margins.left]);

	return (
		<div>
			{countStates.map(({ state, count }, i) => {
				const isSelected = selectedState === state;
				return (
					<RadioBar
						key={i}
						width={width}
						state={state}
						count={count}
						barWidth={xScale(count)}
						isSelected={isSelected}
						index={i}
						onClick={() => {
							setSelectedState("filterState", state);
						}}
					/>
				);
			})}
		</div>
	);
}

StateFilter.propTypes = {
	dataset: PropTypes.array.isRequired,
	width: PropTypes.number.isRequired,
	filterParameters: PropTypes.string,
	setFilterParameters: PropTypes.func.isRequired,
};
