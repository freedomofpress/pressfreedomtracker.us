import React from 'react'
import '../../sass/ChartDescription.sass'

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
