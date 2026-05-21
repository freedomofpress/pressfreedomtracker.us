import React from 'react'
import Button from './Button'
import DropdownButton from './DropdownButton'
import { toNumbers } from 'canvg'

const labelStyle = {
	fontFamily: 'var(--font-base)',
	fontSize: '18px',
}

export default function ButtonsRow({
	label,
	buttonLabels,
	dropDownLabels = [],
	defaultSelection = null,
	updateSelection,
	isButtonSelectable,
	tooltipIfUnselectable = null,
}) {
	const [selectedButton, setSelectedButton] = React.useState(null)
	// Remember the last value picked from the dropdown so it stays visible
	// even after the user clicks a preset button.
	const [lastDropdownValue, setLastDropdownValue] = React.useState(null)

	function changeSelectedButton(buttonLabel) {
		updateSelection(buttonLabel)
		setSelectedButton(buttonLabel)
		if (dropDownLabels.includes(buttonLabel)) {
			setLastDropdownValue(buttonLabel)
		}
	}

	return (
		<div style={{ display: 'flex', alignItems: 'center', margin: 12 }}>
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
						selected={
							(defaultSelection === buttonLabel && selectedButton === null) ||
							selectedButton === buttonLabel
						}
						onClick={() => {
							changeSelectedButton(buttonLabel)
						}}
						selectable={isButtonSelectable(buttonLabel)}
						tooltipIfUnselectable={tooltipIfUnselectable}
						key={buttonLabel}
					/>
				))}
				{dropDownLabels.length > 0 && (
					<DropdownButton
						value={dropDownLabels.includes(selectedButton) ? selectedButton : (lastDropdownValue ?? dropDownLabels[0])}
						selected={
							dropDownLabels.includes(selectedButton) ? selectedButton : ""
						}
						onChange={(e) => changeSelectedButton(Number(e))}
						selectable={dropDownLabels}
					/>
				)}
			</div>
		</div>
	)
}
