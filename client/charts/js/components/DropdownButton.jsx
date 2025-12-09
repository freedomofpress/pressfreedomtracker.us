import React from 'react'

const textStyle = {
	fontFamily: 'var(--font-base)',
	fontWeight: '500',
	fontSize: '14px',
}

const ArrowDownSVG = ({stroke}) => (
	<svg width="10" height="6" viewBox="0 0 24 15" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path
			d="M22 2L12 12L2 2"
			stroke={stroke || 'black'}
			strokeWidth="3"
		/>
	</svg>
)

export default function DropdownButton({ selected, selectable = true, onChange }) {
	const [hovered, setHovered] = React.useState(false)

	return (
		<div style={{display:'inline-block', position:'relative'}}>
			<select
				className='btn btn-bordered'
				style={{
					marginBottom: 3,
					backgroundColor: selected || (hovered && selectable) ? 'black' : 'white',
					color: selected || (hovered && selectable) ? 'white' : selectable ? 'black' : 'grey',
					cursor: selectable ? 'pointer' : 'default',
					minWidth: 50,
					fontFamily: textStyle.fontFamily,
					fontSize: textStyle.fontSize,
					fontWeight: textStyle.fontWeight,
					position: 'relative',
					borderRadius: 0,
					paddingRight: '2rem',
					appearance: 'none',
					WebkitAppearance: 'none',
					MozAppearance: 'none',
				}
				}
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
				{
					Array.isArray(selectable) &&
					selectable.map((option) => (
						<option key={option} value={option}>
							{option}
						</option>
					))
				}
			</select >
			<div
				aria-hidden={true}
				style={{
					position: 'absolute',
					right: '0.875rem',
					top: '48%',
					transform: 'translateY(-50%)',
					pointerEvents: 'none',
					display: 'flex',
					alignItems: 'center',
					zIndex: 99,
				}}
			>
				<ArrowDownSVG stroke={selected || (hovered && selectable) ? 'white' : selectable ? 'black' : 'grey'} />
			</div>
		</div>
	)
}
