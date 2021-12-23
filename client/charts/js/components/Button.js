import React from "react";

const textStyle = {
	fontFamily: "Helvetica Neue",
	fontWeight: "500",
	fontSize: "14px",
};

export function Button({ label, selected, selectable = true, onClick }) {
	const [hovered, setHovered] = React.useState(false);
	return (
		<button
			style={{
				padding: 8,
				border: "none",
				marginBottom: 3,
				outline: "solid 3px black",
				backgroundColor:
					selected || (hovered && selectable) ? "black" : "white",
				color:
					selected || (hovered && selectable)
						? "white"
						: selectable
						? "black"
						: "grey",
				cursor: selectable ? "pointer" : "default",
			}}
			onClick={() => {
				if (selectable) {
					onClick();
				}
			}}
			onMouseEnter={() => {
				setHovered(true);
			}}
			onMouseLeave={() => {
				setHovered(false);
			}}
		>
			<p
				style={{
					margin: 0,
					fontFamily: textStyle.fontFamily,
					fontSize: textStyle.fontSize,
					fontWeight: textStyle.fontWeight,
				}}
			>
				{label}
			</p>
		</button>
	);
}
