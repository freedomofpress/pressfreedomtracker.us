import React from "react";
import classNames from "classnames";

export default function CategorySection({
	symbol,
	label,
	count,
	isOpen,
	onClick,
	children,
}) {
	return (
		<div
			className={classNames("category-checkbox", {
				"category-checkbox--disabled": count === 0,
			})}
		>
			<input
				className="category-checkbox--input"
				type="checkbox"
				id={symbol}
				checked={isOpen}
				onChange={() => onClick(label)}
			/>
			<label htmlFor={symbol} className="category-checkbox--label">
				<span className={`category category-${symbol}`}>{label}</span>
				<span>{count}</span>
			</label>
			{isOpen && <>{children}</>}
		</div>
	);
}
