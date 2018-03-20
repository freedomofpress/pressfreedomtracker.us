import React, { PureComponent } from 'react'
import FilterAccordion from '~/filtering/FilterAccordion'


class FiltersBody extends PureComponent {
	render() {
		const {
			selectedAccordions,
			handleAccordionSelection,
			filtersByCategory,
			handleFilterChange,
			filterValues,
			noCategoryFiltering,
			choices,
		} = this.props
		return (
			<ul className="filters__body">
				{filtersByCategory.map(category => (
					<FilterAccordion
						key={category.id}
						category={category}
						handleAccordionSelection={handleAccordionSelection}
						handleFilterChange={handleFilterChange}
						selectedAccordions={selectedAccordions}
						filterValues={filterValues}
						noCategoryFiltering={noCategoryFiltering}
						choices={choices}
					/>
				))}
			</ul>
		)
	}
}


export default FiltersBody
