import React, { PureComponent } from 'react'
import FilterAccordion from '~/filtering/FilterAccordion'


class FiltersBody extends PureComponent {
	render() {
		const {
			selectedAccordions,
			handleAccordionSelection,
			categoriesEnabled,
			handleFilterChange,
			filterValues,
			noCategoryFiltering,
			choices,
		} = this.props
		return (
			<ul className="filters__body">
				<FilterAccordion
					category={{
						id: -1,
						title: 'General',
						enabled: true,
					}}
					handleAccordionSelection={handleAccordionSelection}
					handleFilterChange={handleFilterChange}
					selectedAccordions={selectedAccordions}
					filterValues={filterValues}
					noCategoryFiltering={noCategoryFiltering}
					choices={choices}
				/>

				{categoriesEnabled.map(category => (
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
