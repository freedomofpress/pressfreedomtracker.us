import React from "react";
import * as d3 from "d3";
import { countBy } from "lodash";

const margins = {
	top: 10,
	left: 50,
	right: 20,
	bottom: 50,
};

export function RadioBars({ data, startDate, endDate, width, height }) {
	const states = countBy(data, (d) => {
		return d.state;
	});

	const countStates = Object.entries(states)
		.map(([state, count]) => ({
			state: state,
			count: count,
		}))
		.sort((a, b) => b.count - a.count);

	const xScale = d3
		.scaleLinear()
		.domain([0, d3.max(countStates.map((d) => d.count))])
		.range([margins.left, width - margins.right]);

	return (
		<div>
			{countStates.map((d, i) => (
				<div
					key={i}
					style={{
						display: "flex",
						flexDirection: "row",
						marginTop: 8,
						marginBottom: 8,
						// marginRight: 150,
						// marginLeft: 150,
					}}
				>
					<div
						style={{
							display: "flex",
							marginRight: 8,
							// backgroundColor: 'red',
						}}
					>
						<input
							type="radio"
							name="drone"
							checked
							style={{ width: 24, height: 24 }}
						/>
					</div>
					<div
						key={d.state}
						style={{
							display: "flex",
							flexDirection: "column",
							// backgroundColor: 'yellow',
							alignItems: "bottom",
							justifyContent: "flex-end",
						}}
					>
						<div
							style={{
								display: "flex",
								flexDirection: "row",
								justifyContent: "space-between",
								marginBottom: 0,
							}}
						>
							<div
								style={{
									color: "black",
									fontSize: 14,
									lineHeight: "20px",
									fontFamily: "sans-serif",
								}}
							>
								{d.state}
							</div>
							<div
								className="axesFontFamily"
								style={{
									fontSize: 12,
									// fontFamily: 'sans-serif',
									// backgroundColor: '#F2F2F2',
									// width: 25,
									justifyContent: "flex-end",
								}}
							>
								{d.count}
							</div>
						</div>

						{/* FIXME - 42 is a magic number representing the width of the radio boxes */}
						<svg width={width - 42} height={4}>
							<rect
								x={0}
								y={0}
								width={xScale(d.count)}
								// width={width - margins.left - margins.right - xScale(d.count)}
								height={4}
								fill={"black"}
							/>
						</svg>
					</div>
				</div>
			))}
		</div>
	);
}
