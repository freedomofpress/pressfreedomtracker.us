import React from 'react'
import PropTypes from 'prop-types'

export default function CategorySection({
	label,
	count,
	isOpen,
	onClick,
	children,
}) {
	return (
		<div className="filters__group">
			<div onClick={() => onClick(label)}>
				{!isOpen && <span>&#9650;</span>}
				{isOpen && <span>&#9660;</span>}
				{label} ({count})
			</div>
			{isOpen && (
				<>
					{children}
				</>
			)}
		</div>
	)
}

CategorySection.propTypes = {
	label: PropTypes.string.isRequired,
	count: PropTypes.number.isRequired,
	isOpen: PropTypes.bool.isRequired,
	onClick: PropTypes.func.isRequired,
	children: PropTypes.node,
}
