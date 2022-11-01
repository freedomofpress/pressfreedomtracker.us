import React from 'react'
import TagFilter from './TagFilter'
import FilterSet from './FilterSet'

export default function GeneralFilter({
	filterDef,
	filterParameters,
	setFilterParameters,
	width,
	dataset,
	filterWithout,
	initialFilterParams,
}) {

	function handleFilterChange(event) {
		setFilterParameters(event.target.name, event.target.value)
	}

	return (
		<>
			<details
				className="filters__group filters__form--category"
				open={Boolean(filterParameters.tags.parameters)}
			>
				<summary className="filters__form-summary">
					<h3 className="filter__heading">Tag</h3>
				</summary>
				<TagFilter
					width={width}
					dataset={dataset}
					filterParameters={filterParameters.tags.parameters}
					initialPickedTags={initialFilterParams.tags.parameters}
				/>
			</details>
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
		</>
	)
}
