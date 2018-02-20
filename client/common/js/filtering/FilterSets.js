import React from 'react'
import {
	AutocompleteInput,
	BoolInput,
	ChoiceInput,
	DateRangeInput,
	TextInput,
	RadioPillInput,
} from '~/filtering/Inputs'


function FilterSet({ children }) {
	return (
		<div className="filters__set">
			{children}
		</div>
	)
}


const FilterSets = {}


FilterSets['General'] = function({ handleFilterChange, filterValues }) {
	return (
		<FilterSet>
			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Search Terms"
				filter="search"
			/>

			<DateRangeInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Took place between"
				filter="date"
			/>

			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Affiliation"
				filter="affiliation"
			/>

			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="City"
				filter="city"
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="State"
				filter="state"
				type="incident.State"
				isSingle={true}
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Targeted any of these journalists"
				filter="targets"
				type="incident.Target"
				isSingle={false}
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Has any of these tags"
				filter="tags"
				type="common.CommonTag"
				isSingle={false}
			/>

			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Lawsuit Name"
				filter="lawsuit_name"
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Venue"
				filter="venue"
				type="incident.Venue"
				isSingle={true}
			/>
		</FilterSet>
	)
}


FilterSets['General'].fields = [
	'search',
	'date_lower',
	'date_upper',
	'affiliation',
	'city',
	'state',
	'targets',
	'tags',
	'lawsuit_name',
	'venue',
]


export default FilterSets
