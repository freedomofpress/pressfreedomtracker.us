import React, { PureComponent } from 'react'
import classNames from 'classnames'


class FiltersCategorySelection extends PureComponent {
	render() {
		const {
			categories,
			categoriesEnabled,
			handleSelection,
		} = this.props

		return (
			<div className="filters__category-selection">
				<div className="filters__text">
					Limit to
				</div>

				<ul className="filters__categories">
					{categories.map(category => (
						<li
							key={category.id}
							className={classNames(
								'filters__category',
								{ 'filters__category--active': categoriesEnabled[category.id] }
							)}
							onClick={handleSelection.bind(null, category.id)}
						>
							{category.title}
						</li>
					))}
				</ul>
			</div>
		)
	}
}


export default FiltersCategorySelection
