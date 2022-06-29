import React, { useState } from 'react'
import * as d3 from 'd3'
import { range } from 'lodash'
import CategoryFilter from './CategoryFilter'
import StateFilter from './StateFilter'
import {
	formatDataset,
	firstDayOfMonth,
	firstDayOfNextMonth,
	removeElement,
	isSubset,
} from '../lib/utilities'
import ButtonsRow from './ButtonsRow'
import TimeMonthsFilter from './TimeMonthsFilter'
import TimeYearsFilter from './TimeYearsFilter'

export default function FiltersIntegration({ width, dataset: dirtyDataset, initialFilterParams, filters: filterDefs }) {
	const dataset = formatDataset(dirtyDataset)

	const [minDate, maxDate] = d3.extent(dataset.map((d) => new Date(d.date)))
	const dateExtents = [firstDayOfMonth(minDate), firstDayOfNextMonth(maxDate)]
	const yearDateExtents = dateExtents.map((date) => date.getUTCFullYear())
	const allYears = range(...yearDateExtents)

	const [filtersParameters, setFitlersParameters] = useState({
		filterCategory: { type: 'category', parameters: [], enabled: true },
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
			enabled: true,
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
		<div className="filter__form">
			<header className="filters__header">
				Filters

				<a
					className="btn btn-ghost"
					href="/all-incidents/"
				>
					Clear All
				</a>
			</header>
			<h3>Categories</h3>
			<div className="chartContainer">
				<CategoryFilter
					width={width}
					height={width / 2}
					dataset={applyFilters(dataset, filterNames)}
					filterDefs={filterDefs.filter(f => f.id !== -1)}
					filterParameters={filtersParameters}
					setFilterParameters={setFilterParameters}
				/>
			</div>
		</div>
	)
}
