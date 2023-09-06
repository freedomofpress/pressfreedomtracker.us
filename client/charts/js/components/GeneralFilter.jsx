import React, { useContext } from 'react'
import TagFilter from './TagFilter'
import FilterSet from './FilterSet'
import { FiltersDispatch } from '../lib/context'
import {
	SET_PARAMETER,
} from '../lib/actionTypes'
import { trackMatomoEvent } from '../lib/utilities'

export default function GeneralFilter({
	filterDef,
	filterParameters,
	setFilterParameters,
	width,
	dataset,
	filterWithout,
	initialFilterParams,
}) {
	const updateFilters = useContext(FiltersDispatch);

	function handleFilterChange(event) {
		updateFilters({
			type: SET_PARAMETER,
			payload: {
				filterName: event.target.name,
				value: event.target.value,
			},
		})
		// Fire matomo event
		trackMatomoEvent(['Filter', event.target.name, 'Change', event.target.value])
	}

	return (
		<>
			<details
				className="filters__group filters__form--category"
				open={Boolean(filterParameters?.tags?.parameters)}
			>
				<summary className="filters__form-summary">
					<h3 className="filter__heading">Tag</h3>
				</summary>
				<TagFilter
					width={width}
					dataset={dataset}
					filterParameters={filterParameters?.tags?.parameters || []}
					initialPickedTags={initialFilterParams?.tags?.parameters || []}
				/>
			</details>
			<div className="filters__form--fieldset filters__form--general">
				<FilterSet
					filters={filterDef?.filters || []}
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
