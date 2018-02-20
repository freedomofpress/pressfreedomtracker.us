import React from 'react'
import classNames from 'classnames'
import { CollapseIcon, ExpandIcon } from '~/filtering/Icons'
import FilterSets from '~/filtering/FilterSets'
import NewFilterSet from '~/filtering/NewFilterSet'


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
	let FilterSet
	if(category.id === -1) {
		// General is a special category with id -1 that should be rendered
		FilterSet = typeof FilterSets[category.title] === 'function' ? FilterSets[category.title] : null
	} else if (!category.related_fields || !(category.related_fields.length > 0)) {
		// Don't bother rendering an accordion with no filters
		return null
	}


	const isActive = selectedAccordions.includes(category.id)
	const collapsible = !noCategoryFiltering

	let renderedFilterset
	if(isActive && category.related_fields) {
		renderedFilterset = (<NewFilterSet
			title={category.title}
			fields={category.related_fields}
			handleFilterChange={handleFilterChange}
			filterValues={filterValues}
			choices={choices}
			key={category.id}
		/>)
	} else if(isActive && FilterSet) {
		renderedFilterset = (
			<FilterSet
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
			/>
		)
	} else {
		renderedFilterset = null
	}

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
					type="button"
				>
					{isActive ? <CollapseIcon /> : <ExpandIcon />}
					{category.title}
				</button>
			)}

			{renderedFilterset}
		</li>
	)
}


export default FilterAccordion
