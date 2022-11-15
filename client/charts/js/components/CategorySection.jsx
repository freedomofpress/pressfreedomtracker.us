import React from 'react'
import PropTypes from 'prop-types'
import classNames from "classnames"

export default function CategorySection({
	symbol,
	label,
	count,
	isOpen,
	onClick,
	children,
}) {
	return (
		<div className={classNames("category-checkbox", {"category-checkbox--disabled": count === 0})}>
			<input
				className="category-checkbox--input"
				type="checkbox"
				id={symbol}
				checked={isOpen}
				onChange={() => onClick(label)}/>
			<label
				htmlFor={symbol}
				className="category-checkbox--label"
			>
				<span className={`category category-${symbol}`}>{label}</span>
				<span>{count}</span>
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
