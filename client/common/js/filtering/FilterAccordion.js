import React from 'react'
import classNames from 'classnames'
import { CollapseIcon, ExpandIcon } from '~/filtering/Icons'
import FilterSets from '~/filtering/FilterSets'


function FilterAccordion({
	category,
	selectedAccordions,
	handleAccordionSelection,
	handleFilterChange,
	filterValues,
	noCategoryFiltering,
	choices,
}) {
	if (!category.enabled) {
		return null
	}

	const FilterSet = typeof FilterSets[category.title] === 'function' ? FilterSets[category.title] : null
	if (!FilterSet) {
		// Don't bother rendering an accordion with no filters
		return null
	}

	const isActive = selectedAccordions.includes(category.id)
	const collapsible = !noCategoryFiltering

	return (
		<li
			className={classNames(
				'filters__accordion-category',
				{ 'filters__accordion-category--no-divider': noCategoryFiltering }
			)}
		>
			{collapsible && (
				<button
					className={classNames(
						'filters__accordion',
						{ 'filters__accordion--active': isActive }
					)}
					onClick={handleAccordionSelection.bind(null, category.id)}
				>
					{isActive ? <CollapseIcon /> : <ExpandIcon />}
					{category.title}
				</button>
			)}

			{isActive && (
				<FilterSet
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					choices={choices}
				/>
			)}
		</li>
	)
}


export default FilterAccordion
