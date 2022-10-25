import React from 'react'
import FilterSet from './FilterSet'

export default function GeneralFilter({
	filterDef,
	filterParameters,
	setFilterParameters,
	width,
	dataset,
	filterWithout,
}) {

	function handleFilterChange(event) {
		setFilterParameters(event.target.name, event.target.value)
	}

	return (
		<div className="filters__form--fieldset filters__form--general">
			<FilterSet
				filters={filterDef.filters}
				filterParameters={filterParameters}
				handleFilterChange={handleFilterChange}
				setFilterParameters={setFilterParameters}
				width={width}
				filterWithout={filterWithout}
				dataset={dataset}
			/>
		</div>
	)
}
