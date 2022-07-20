import React from 'react'
import PropTypes from 'prop-types'

export default function CategorySection({
	symbol,
	label,
	count,
	isOpen,
	onClick,
	children,
}) {
	return (
		<div className="category-checkbox">
			<input type="checkbox" id={symbol} onClick={() => onClick(label)}/>
			<label
				htmlFor={symbol}
				className={`category category-${symbol}`}
			>
				{label} ({count})
			</label>
			{isOpen && (
				<>
					{children}
				</>
			)}
		</div>
	)
}

CategorySection.propTypes = {
	symbol: PropTypes.string.isRequired,
	label: PropTypes.string.isRequired,
	count: PropTypes.number.isRequired,
	isOpen: PropTypes.bool.isRequired,
	onClick: PropTypes.func.isRequired,
	children: PropTypes.node,
}
