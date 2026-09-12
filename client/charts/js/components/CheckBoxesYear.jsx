import React from "react";
import PropTypes from "prop-types";

export default function CheckBoxesYear({
	width,
	options,
	selectedYears,
	onClick,
}) {
	const side = 20;

	return (
		<div style={{ width, display: "flex", flexDirection: "column" }}>
			{options.map((d) => (
				<div key={d.year}>
					<div
						style={{
							display: "flex",
							flexDirection: "row",
							justifyContent: "space-between",
						}}
					>
						<div
							style={{
								display: "flex",
								flexDirection: "row",
								fontSize: 14,
								alignItems: "center",
								marginBottom: 16,
							}}
						>
							<input
								type="checkbox"
								style={{ width: side, height: side }}
								checked={selectedYears.includes(d.year)}
								onChange={() => onClick(d)}
							/>

							<div
								style={{
									flexDirection: "row",
									marginLeft: 10,
									fontFamily: "var(--font-base)",
								}}
							>
								{d.year}
							</div>
						</div>

						<div
							style={{
								display: "flex",
								fontSize: 12,
								height: 15,
								fontFamily: "Helvetica Neue",
								backgroundColor: selectedYears.includes(d.year)
									? "#F2FC67"
									: "white",
								padding: 3,
							}}
						>
							{d.count}
						</div>
					</div>
				</div>
			))}
		</div>
	);
}

CheckBoxesYear.propTypes = {
	width: PropTypes.number.isRequired,
	options: PropTypes.arrayOf(
		PropTypes.shape({
			year: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
				.isRequired,
			count: PropTypes.number,
		}),
	).isRequired,
	selectedYears: PropTypes.array.isRequired,
	onClick: PropTypes.func.isRequired,
};
