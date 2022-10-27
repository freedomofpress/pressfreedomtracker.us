import React, { useReducer, createContext} from 'react'
import * as d3 from 'd3'
import CategoryFilter from './CategoryFilter'
import GeneralFilter from './GeneralFilter'
import {
	TOGGLE_PARAMETER_ITEM,
	SET_PARAMETER,
	DELETE_PARAMETER_ITEMS,
} from '../lib/actionTypes'
import { FiltersDispatch } from '../lib/context'
import {
	formatDataset,
	firstDayOfMonth,
	firstDayOfNextMonth,
	removeElement,
	isSubset,
	rangeInclusive,
	difference,
} from '../lib/utilities'


function filterReducer(state, {type, payload}) {
	switch (type) {
		case TOGGLE_PARAMETER_ITEM:
			let { item } = payload
			let old = state[payload.filterName].parameters
			if (old.has(item)) {
				old.delete(item)
			} else {
				old.add(item)
			}
			return {...state}
		case DELETE_PARAMETER_ITEMS:
			let { items } = payload

			state[payload.filterName].parameters = difference(
				state[payload.filterName].parameters,
				new Set(items),
			)
			return {...state}

		case SET_PARAMETER:
			state[payload.filterName].parameters = payload.value
			return {...state}
		default:
		    throw new Error(`Unknown action type: ${type}`)
	}
}


export default function FiltersIntegration({ width, dataset: dirtyDataset, initialFilterParams, filters: filterDefs }) {
	const dataset = formatDataset(dirtyDataset)

	const [minDate, maxDate] = d3.extent(dataset.map((d) => new Date(d.date)))
	const dateExtents = [firstDayOfMonth(minDate), firstDayOfNextMonth(maxDate)]
	const yearDateExtents = dateExtents.map((date) => date.getUTCFullYear())
	const allYears = rangeInclusive(...yearDateExtents, 1)


	const [filtersParameters, updateFilters] = useReducer(filterReducer, {
		filterTimeMonths: {
			type: 'timeMonths',
			parameters: {
				min: minDate,
				max: maxDate,
			},
			enabled: true,
		},
		filterTimeYears: {
			type: 'timeYears',
			parameters: [...allYears],
			enabled: false,
		},
		filterState: { type: 'state', parameters: 'All', enabled: true },
		...initialFilterParams
	})

	function getFilteringExpression(filterName) {
		if (filtersParameters[filterName].enabled) {
			switch (filterName) {
				case 'categories':
					return (d) => isSubset(
						Array.from(filtersParameters[filterName].parameters),
						d.categories
					)
				case 'filterTimeMonths':
					return (d) =>
						new Date(d.date).getTime() >= filtersParameters[filterName].parameters.min.getTime() &&
						new Date(d.date).getTime() <= filtersParameters[filterName].parameters.max.getTime()
				case 'filterTimeYears':
					return (d) =>
						filtersParameters[filterName].parameters.includes(d.date.getUTCFullYear())
				case 'filterState':
					return (d) =>
						filtersParameters[filterName].parameters === 'All' ||
						d.state === filtersParameters[filterName].parameters
				case 'tags':
					return (d) => isSubset(
						Array.from(filtersParameters[filterName].parameters),
						d.tags,
					)
			}
		} else {
			return () => true
		}
	}

	function applyFilter(dataset, filterName) {
		const filterCondition = getFilteringExpression(filterName)
		return dataset.filter(filterCondition)
	}

	function applyFilters(dataset, filterNames) {
		return filterNames.reduce(
			(previousValue, currentValue) => applyFilter(previousValue, currentValue),
			dataset
		)
	}

	function makeUrlParams() {
		const searchParams = new URLSearchParams("")

		let categories = []
		filterDefs.forEach(category => {
			if (category.id === -1 || filtersParameters.categories.parameters.has(category.title)) {
				if (category.id !== -1) {
					categories.push(category.title)
				}
				category.filters.forEach( ({name, type})=> {
					let filter = filtersParameters[name]
					if (filter && filter.parameters) {
						if (filter.type === 'autocomplete' || filter.type === 'choice' || filter.type === 'bool' || filter.type === 'radio' || filter.type === 'text') {
							searchParams.append(name, filter.parameters)
						} else if (filter.type === 'date') {
							if (filter.parameters.min) {
								searchParams.append(`${name}_lower`, filter.parameters.min?.toISOString()?.substring(0, 10))
							}
							if (filter.parameters.max) {
								searchParams.append(`${name}_upper`, filter.parameters.max?.toISOString()?.substring(0, 10))
							}
						}
					}
				})
			}
		})
		searchParams.append('categories', categories.join(','))
		return searchParams.toString()
	}

	const filterNames = Object.keys(filtersParameters)
	const filterWithout = Object.fromEntries(
		filterNames.map((filterName) => [
			filterName,
			(dataset) => {
				const filtersToApply = removeElement(filterNames, filterName)
				return applyFilters(dataset, filtersToApply)
			},
		])
	)

	return (
		<FiltersDispatch.Provider value={updateFilters}>
			<section className="filters__form" aria-labelledby="filter-sidebar-heading">
				<div className="filters__form--header">
					<h2 className="filter__heading" id="filter-sidebar-heading">Filters</h2>
					<a
						className="btn btn-ghost"
						href="/all-incidents/"
					>
						Clear All
					</a>
				</div>
				<details className="filters__group filters__form--category" open>
					<summary className="filters__form-summary">
						<h3 className="filter__heading">Category</h3>
					</summary>
					<CategoryFilter
						width={width}
						height={width / 1.5}
						dataset={applyFilters(dataset, filterNames)}
						filterDefs={filterDefs.filter(f => f.id !== -1)}
						filterParameters={filtersParameters}
						filterWithout={filterWithout}
					/>
				</details>
				<GeneralFilter
					filterDef={filterDefs.filter(f => f.id === -1)[0]}
					filterParameters={filtersParameters}
					width={width}
					dataset={dataset}
					filterWithout={filterWithout}
				/>
				<div className="filters__form-actions">
					<button
						className="btn btn-secondary filters__form--submit"
						type="submit"
						onClick={() => {
							const url = new URL(window.location);
							url.search = makeUrlParams()
							window.location = url.toString()
						}}
					>Apply filters</button>
				</div>

				<div className="incident-index__filters-mobile-controls">
					<a className="incident-index__filters-mobile-clear" href="{{ page.url }}">Clear All</a>
					<button
						className="btn btn-secondary filters__form--submit"
						type="submit"
						onClick={() => {
							const url = new URL(window.location);
							url.search = makeUrlParams()
							window.location = url.toString()
						}}
					>Apply filters</button>
				</div>
			</section>
		</FiltersDispatch.Provider>
	)
}
