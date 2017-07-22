import React, { PureComponent } from 'react'
import CategoryList from '~/filtering/CategoryList'
import FiltersList from '~/filtering/FiltersList'


class FilterSummary extends PureComponent {
	render() {
		const {
			filtersExpanded,
			filterValues,
			categoriesEnabled,
			changeFiltersMessage,
		} = this.props

		const hasAnyFilters = (
			Object.keys(filterValues).length > 0 ||
			categoriesEnabled.some(category => {
				// Check if a non-General category has been whitelisted.
				return category.id !== -1 && category.enabled
			})
		)

		if (!hasAnyFilters) {
			return (
				<div className="filters__summary filters__text--dim">
					{changeFiltersMessage || 'No filters applied.'}
				</div>
			)
		}

		if (filtersExpanded) {
			return (
				<div className="filters__summary">
					Filters
				</div>
			)
		}

		const categories = categoriesEnabled.filter(({ enabled }) => enabled)
		const hasFilters = Object.keys(filterValues).length > 0

		return (
			<div className="filters__summary filters__summary--can-compact filters__text--dim">
				Showing <CategoryList categories={categories} />
				{hasFilters && ' '}
				{hasFilters && <FiltersList filterValues={filterValues} />}
			</div>
		)
	}
}


export default FilterSummary
