import React from 'react'

const RADIO_BOX_WIDTH = 35

export default function RadioBar({ state, count, i, onClick, isSelected, barWidth, width }) {
	return (
		<div
			style={{
				display: 'flex',
				flexDirection: 'row',
				marginTop: 12,
				marginBottom: 12,
			}}
		>
			<div
				style={{
					display: 'flex',
					flexDirection: 'row-reverse',
					width: RADIO_BOX_WIDTH,
				}}
			>
				<input
					type="radio"
					name="drone"
					checked={isSelected}
					onChange={onClick}
					style={{ width: 24, height: 24 }}
				/>
			</div>

			<div
				style={{
					display: 'flex',
					flexDirection: 'column',
					justifyContent: 'flex-end',
				}}
			>
				<div
					style={{
						display: 'flex',
						flexDirection: 'row',
						justifyContent: 'space-between',
						marginBottom: 0,
					}}
				>
					<div
						style={{
							color: 'black',
							fontSize: 14,
							lineHeight: '20px',
							fontFamily: 'var(--font-base)',
						}}
					>
						{state}
					</div>
					<div
						style={{
							fontFamily: 'var(--font-mono)',
							fontSize: 12,
							justifyContent: 'flex-end',
							backgroundColor: isSelected ? '#F2FC67' : null,
							padding: 3,
						}}
					>
						{count}
					</div>
				</div>
				<div style={{ width: width - RADIO_BOX_WIDTH, height: 4 }}>
					<div
						style={{
							zIndex: -1,
							width: barWidth,
							height: 3,
							border: '1px solid black',
							backgroundColor: 'black',
							transition: 'all 250ms ',
						}}
					/>
					<div
						style={{
							top: -4,
							left: 1,
							position: 'relative',
							width: isSelected ? barWidth : 0,
							height: 3,
							backgroundColor: '#F2FC67',
							transition: 'all 250ms ',
						}}
					/>
				</div>
			</div>
		</div>
	)
}
