import React, { useState } from 'react'
import * as d3 from 'd3'
import CategoryFilter from './CategoryFilter'
import StateFilter from './StateFilter'
import GeneralFilter from './GeneralFilter'
import {
	formatDataset,
	firstDayOfMonth,
	firstDayOfNextMonth,
	removeElement,
	isSubset,
	rangeInclusive,
} from '../lib/utilities'
import ButtonsRow from './ButtonsRow'
import TimeMonthsFilter from './TimeMonthsFilter'
import TimeYearsFilter from './TimeYearsFilter'

export default function FiltersIntegration({ width, dataset: dirtyDataset, initialFilterParams, filters: filterDefs }) {
	const dataset = formatDataset(dirtyDataset)

	const [minDate, maxDate] = d3.extent(dataset.map((d) => new Date(d.date)))
	const dateExtents = [firstDayOfMonth(minDate), firstDayOfNextMonth(maxDate)]
	const yearDateExtents = dateExtents.map((date) => date.getUTCFullYear())
	const allYears = rangeInclusive(...yearDateExtents, 1)

	const [filtersParameters, setFitlersParameters] = useState({
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

	function setFilterParameters(filterName, newFilterParameters) {
		if (typeof newFilterParameters === 'function') {
			setFitlersParameters((oldFilters) => {
				const newParameters = oldFilters
				const oldFilterParameters = oldFilters[filterName].parameters
				newParameters[filterName].parameters = newFilterParameters(oldFilterParameters)
				return { ...newParameters }
			})
		} else {
			const newParameters = filtersParameters
			newParameters[filterName].parameters = newFilterParameters
			setFitlersParameters({ ...newParameters })
		}
	}

	function setFilterEnabling(filterName, isEnabled) {
		const newFilterParameters = filtersParameters
		newFilterParameters[filterName].enabled = isEnabled
		setFitlersParameters({ ...newFilterParameters })
	}

	function getFilteringExpression(filterName) {
		if (filtersParameters[filterName].enabled) {
			switch (filterName) {
				case 'filterCategory':
					return (d) => isSubset(filtersParameters[filterName].parameters, d.categories)
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
			}
		} else {
			return () => true
		}
	}

	const [timeChartType, setTimeChartType] = useState('Months')

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
			if (category.id === -1 || filtersParameters.filterCategory.parameters.includes(category.title)) {
				if (category.id !== -1) {
					categories.push(category.id)
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
					setFilterParameters={setFilterParameters}
				/>
			</details>
			<GeneralFilter
				filterDef={filterDefs.filter(f => f.id === -1)[0]}
				filterParameters={filtersParameters}
				setFilterParameters={setFilterParameters}
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

			<div class="incident-index__filters-mobile-controls">
				<a class="incident-index__filters-mobile-clear" href="{{ page.url }}">Clear All</a>
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
	)
}
