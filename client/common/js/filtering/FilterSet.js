import React, { PureComponent } from 'react'
import {
	AutocompleteInput,
	BoolInput,
	ChoiceInput,
	DateRangeInput,
	TextInput,
	RadioPillInput,
} from '~/filtering/Inputs'

function FilterSet({ title, filters, handleFilterChange, filterValues }) {
		const components = filters.map((filter, index) => {
			if(filter.type === 'choice' ) {
				return <ChoiceInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					choices={filter.choices}
					key={index}
				/>
			} else if (filter.type === 'date') {
				return <DateRangeInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					key={index}
				/>
			} else if (filter.type === 'text') {
				return <TextInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					key={index}
				/>
			} else if (filter.type === 'radio') {
				return <RadioPillInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					key={index}
				/>
			} else if (filter.type === 'bool') {
				return <BoolInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={`${filter.title}`}
					filter={filter.name}
					key={index}
				/>
			} else if (filter.type === 'autocomplete'){
				return <AutocompleteInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					type={filter.autocomplete_type}
					isSingle={!filter.many}
					key={index}
				/>
			} else {
				console.error('Unknown filter type.')
				return null
			}

		})
		return (
			<div className="filters__set">
				{components}
			</div>
		)
}


export default FilterSet
