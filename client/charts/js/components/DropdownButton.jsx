import React from 'react'

const textStyle = {
	fontFamily: 'var(--font-base)',
	fontWeight: '500',
	fontSize: '14px',
}

export default function DropdownButton({ selected, selectable = true, onChange }) {
	const [hovered, setHovered] = React.useState(false)

	return (
		<select
			className="btn btn-bordered"
			style={{
				marginBottom: 3,
				backgroundColor: selected || (hovered && selectable) ? 'black' : 'white',
				color: selected || (hovered && selectable) ? 'white' : selectable ? 'black' : 'grey',
				cursor: selectable ? 'pointer' : 'default',
				minWidth: 50,
				fontFamily: textStyle.fontFamily,
				fontSize: textStyle.fontSize,
				fontWeight: textStyle.fontWeight,
				padding: '8px',
				borderRadius: 0, // Changed from 4 to 0 for sharp corners
				appearance: 'none',
			}}
			onMouseDown={(e) => {
				if (selectable) {
					onChange(e.target.value)
				}
			}}
			onChange={(e) => {
				if (selectable) {
					onChange(e.target.value)
				}
			}}
			onMouseEnter={(e) => {
				setHovered(true)
			}}
			onMouseLeave={() => {
				setHovered(false)
			}}
			disabled={!selectable}
			value={selected}
		>
			{Array.isArray(selectable) &&
				selectable.map((option) => (
					<option key={option} value={option}>
						{option}
					</option>
				))}
		</select>
	)
}
