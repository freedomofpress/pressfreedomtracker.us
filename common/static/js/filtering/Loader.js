import React from 'react'


export function HorizontalLoader({ className }) {
	return (
		<div className={`horizontal-loader ${className}`}>
			<span className="horizontal-loader__circle"></span>
			<span className="horizontal-loader__circle"></span>
			<span className="horizontal-loader__circle"></span>
		</div>
	)
}


HorizontalLoader.defaultProps = {
	className: '',
}
