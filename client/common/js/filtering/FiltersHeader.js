import React, { PureComponent } from 'react'
import FilterSummary from '~/filtering/FilterSummary'
import { SettingsIcon } from '~/filtering/Icons'


class FiltersHeader extends PureComponent {
	render() {
		const {
			categories,
			categoriesEnabled,
			changeFiltersMessage,
			filtersExpanded,
			filterValues,
			handleToggle,
		} = this.props


		return (
			<div className="filters__header">
				<FilterSummary
					filtersExpanded={filtersExpanded}
					filterValues={filterValues}
					categories={categories}
					categoriesEnabled={categoriesEnabled}
					changeFiltersMessage={changeFiltersMessage}
				/>

				<button
					className="filters__button filters__button--summary-toggle"
					onClick={handleToggle}
					type="button"
				>
					<SettingsIcon />

					{filtersExpanded ? 'Collapse Filters' : 'Change Filters'}
				</button>
			</div>
		)
	}
}


export default FiltersHeader
