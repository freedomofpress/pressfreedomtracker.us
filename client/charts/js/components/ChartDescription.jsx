import React from 'react'
import '../../scss/ChartDescription.scss'

export default function ChartDescription({ id, children }) {
	return (
		<div
			id={id}
			className='chartDescription'
		>
			{children}
		</div>
	)
}
