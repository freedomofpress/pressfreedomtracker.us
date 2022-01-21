import React from 'react'
import { Button } from './Button.js'

const labelStyle = {
  fontFamily: 'sans-serif',
  fontSize: '18px',
}

export function ButtonsRow({
  label,
  buttonLabels,
  defaultSelection = null,
  updateSelection,
  isButtonSelectable,
}) {
  const [selectedButton, setSelectedButton] = React.useState(null)

  function changeSelectedButton(buttonLabel) {
    updateSelection(selectedButton === buttonLabel ? defaultSelection : buttonLabel)
    selectedButton === buttonLabel
      ? setSelectedButton(defaultSelection)
      : setSelectedButton(buttonLabel)
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
            key={buttonLabel}
          />
        ))}
      </div>
    </div>
  )
}
