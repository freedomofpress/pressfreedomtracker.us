import React from 'react'
import Tooltip from './Tooltip'

const textStyle = {
	fontFamily: 'var(--font-base)',
	fontWeight: '500',
	fontSize: '14px',
}

export default function Button({ label, selected, selectable = true, onClick, tooltipIfUnselectable = null }) {
	const [hovered, setHovered] = React.useState(false)
	const [tooltipPosition, setTooltipPosition] = React.useState({ x: 0, y: 0 })

	const updateTooltipPosition = (MouseEvent) => {
		setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
	}

	return (
		<>
		{hovered && !selectable && tooltipIfUnselectable && (
			<Tooltip
				x={tooltipPosition.x}
				y={tooltipPosition.y}
				content={
					<div style={{ fontFamily: 'var(--font-base)', fontSize: 12, fontWeight: 500 }}>
						{tooltipIfUnselectable}
					</div>
				}
			/>
		)}
		<button
			style={{
				padding: 8,
				border: 'none',
				marginBottom: 3,
				outline: 'solid 3px black',
				backgroundColor: selected || (hovered && selectable) ? 'black' : 'white',
				color: selected || (hovered && selectable) ? 'white' : selectable ? 'black' : 'grey',
				cursor: selectable ? 'pointer' : 'default',
				minWidth: 50,
			}}
			onMouseMove={updateTooltipPosition}
			onClick={() => {
				if (selectable) {
					onClick()
				}
			}}
			onMouseEnter={(e) => {
				updateTooltipPosition(e)
				setHovered(true)
			}}
			onMouseLeave={() => {
				setHovered(false)
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
	</>
	)
}
