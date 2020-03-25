import React, { PropTypes } from 'react'
import {
	AutocompleteInput,
	BoolInput,
	ChoiceInput,
	DateRangeInput,
	IntInput,
	TextInput,
	RadioPillInput,
} from '~/filtering/Inputs'

function FilterSet({ filters, handleFilterChange, filterValues }) {
	const components = filters.map((filter, index) => {
		if (filter.type === 'choice') {
			return (
				<ChoiceInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					choices={filter.choices}
					key={index}
				/>
			)
		} else if (filter.type === 'date') {
			return (
				<DateRangeInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					key={index}
				/>
			)
		} else if (filter.type === 'text') {
			return (
				<TextInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					key={index}
				/>
			)
		} else if (filter.type === 'radio') {
			return (
				<RadioPillInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					key={index}
				/>
			)
		} else if (filter.type === 'bool') {
			return (
				<BoolInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={`${filter.title}`}
					filter={filter.name}
					key={index}
				/>
			)
		} else if (filter.type === 'int') {
			return (
				<IntInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={`${filter.title}`}
					filter={filter.name}
					key={index}
					units={filter.units}
				/>
			)
		} else if (filter.type === 'autocomplete') {
			return (
				<AutocompleteInput
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
					label={filter.title}
					filter={filter.name}
					type={filter.autocomplete_type}
					isSingle={!filter.many}
					key={index}
				/>
			)
		}
		console.error('Unknown filter type.')
		return null
	})
	return (
		<div className="filters__set">
			{components}
		</div>
	)
}


FilterSet.propTypes = {
	filters: PropTypes.array.isRequired,
	handleFilterChange: PropTypes.func.isRequired,
	filterValues: PropTypes.object.isRequired,
}


export default FilterSet
