import React from 'react'


function CategoryList({ categories }) {
	return (
		<ul className="filters__summary-list">
			{categories.map(category => (
				<li key={category.id} className="filters__summary-item filters__summary-item--semicolons">
					{category.title}
				</li>
			))}
		</ul>
	)
}


export default CategoryList
