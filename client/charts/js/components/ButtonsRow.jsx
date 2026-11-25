import React from "react";
import Button from "./Button";
import DropdownButton from "./DropdownButton";

const labelStyle = {
	fontFamily: "var(--font-base)",
	fontSize: "18px",
};

export default function ButtonsRow({
	label,
	buttonLabels,
	dropDownLabels = [],
	defaultSelection = null,
	updateSelection,
	isButtonSelectable,
	tooltipIfUnselectable = null,
}) {
	const [selectedButton, setSelectedButton] = React.useState(null);
	const [lastDropdownValue, setLastDropdownValue] = React.useState(null);
	const activeSelection = selectedButton ?? defaultSelection;
	const dropdownSelected = dropDownLabels.includes(activeSelection);

	function changeSelectedButton(buttonLabel) {
		updateSelection(buttonLabel);
		setSelectedButton(buttonLabel);
		if (dropDownLabels.includes(buttonLabel)) {
			setLastDropdownValue(buttonLabel); // maintain dropdown val when changing selection
		}
	}

	return (
		<div style={{ display: "flex", alignItems: "center", margin: 12 }}>
			<div
				style={{
					...labelStyle,
				}}
			>
				{label}
			</div>
			<div style={{ marginLeft: 10 }}>
				{buttonLabels.map((buttonLabel) => (
					<Button
						label={buttonLabel}
						selected={activeSelection === buttonLabel}
						onClick={() => {
							changeSelectedButton(buttonLabel);
						}}
						selectable={isButtonSelectable(buttonLabel)}
						tooltipIfUnselectable={tooltipIfUnselectable}
						key={buttonLabel}
					/>
				))}
				{dropDownLabels.length > 0 && (
					<DropdownButton
						value={
							dropdownSelected
								? activeSelection
								: (lastDropdownValue ?? dropDownLabels[0])
						}
						selected={dropdownSelected ? activeSelection : ""}
						onChange={(e) => changeSelectedButton(Number(e))}
						selectable={dropDownLabels}
					/>
				)}
			</div>
		</div>
	);
}
