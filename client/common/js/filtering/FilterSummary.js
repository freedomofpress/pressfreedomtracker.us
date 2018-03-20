import React, { PureComponent } from 'react'
import CategoryList from '~/filtering/CategoryList'
import FiltersList from '~/filtering/FiltersList'


class FilterSummary extends PureComponent {
	render() {
		const {
			categories,
			categoriesEnabled,
			changeFiltersMessage,
			filtersExpanded,
			filterValues,
		} = this.props

		const hasFilters = Object.keys(filterValues).length > 0

		if (!hasFilters) {
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


		return (
			<div className="filters__summary filters__summary--can-compact filters__text--dim">
				Showing <CategoryList categories={categories.filter(({ id }) => categoriesEnabled[id])} />
				{' '}
				<FiltersList
					categories={categories}
					categoriesEnabled={categoriesEnabled}
					filterValues={filterValues}
				/>
			</div>
		)
	}
}


export default FilterSummary
