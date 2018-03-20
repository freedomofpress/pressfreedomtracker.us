import React from 'react'

import { GENERAL_ID } from '~/filtering/constants'


function CategoryList({ categories }) {
	return (
		<ul className="filters__summary-list">
			{categories.filter(({ id }) => id !== GENERAL_ID).map(category => (
				<li key={category.id} className="filters__summary-item filters__summary-item--semicolons">
					{category.title}
				</li>
			))}
		</ul>
	)
}


export default CategoryList
