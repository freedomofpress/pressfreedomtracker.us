import React, { PureComponent } from 'react'
import axios from 'axios'
import queryString from 'query-string'
import moment, { isMoment } from 'moment'

import {
	ALL_FILTERS,
	AUTOCOMPLETE_SINGLE_FILTERS,
	AUTOCOMPLETE_MULTI_FILTERS,
	DATE_FILTERS,
	DATE_FORMAT,
} from '~/filtering/constants'
import FiltersCategorySelection from '~/filtering/FiltersCategorySelection'
import FiltersHeader from '~/filtering/FiltersHeader'
import FiltersExpandable from '~/filtering/FiltersExpandable'
import FiltersBody from '~/filtering/FiltersBody'
import FiltersFooter from '~/filtering/FiltersFooter'
import FilterSets from '~/filtering/FilterSets'


function Filters({ children }) {
	return <div className="filters">{children}</div>
}

class IncidentFiltering extends PureComponent {
	constructor(props, ...args) {
		super(props, ...args)

		this.handleToggle = this.handleToggle.bind(this)
		this.handleSelection = this.handleSelection.bind(this)
		this.handleApplyFilters = this.handleApplyFilters.bind(this)
		this.handleClearFilters = this.handleClearFilters.bind(this)
		this.handleAccordionSelection = this.handleAccordionSelection.bind(this)
		this.handleFilterChange = this.handleFilterChange.bind(this)
		this.handlePopState = this.handlePopState.bind(this)

		const selectedAccordions = [-1]
		if (props.noCategoryFiltering && props.category) {
			selectedAccordions.push(props.category)
		}

		this.state = {
			filtersExpanded: false,
			selectedAccordions,
			loading: 0,
			filtersTouched: false,
			...this.getStateFromQueryParams(),
		}
	}

	componentDidMount() {
		window.addEventListener('popstate', this.handlePopState)
	}

	componentWillUnmount() {
		window.removeEventListener('popstate', this.handlePopState)
	}

	getStateFromQueryParams() {
		const params = queryString.parse(location.search)

		const categoriesEnabledById = (params.categories || '').split(',').map(n => parseInt(n))
		const categoriesEnabled = this.props.availableCategories.map(category => {
			const enabled = (
				categoriesEnabledById.includes(category.id) ||
				this.props.category === category.id
			)
			return {
				...category,
				enabled,
			}
		})

		const filterValues = Object.keys(params).reduce((values, key) => {
			if (!ALL_FILTERS.includes(key)) {
				return values
			}

			if (DATE_FILTERS.includes(key)) {
				var value = moment(params[key])
			} else if (AUTOCOMPLETE_MULTI_FILTERS.includes(key)) {
				var value = params[key]
					.split(',')
					.map(n => { return { id: parseInt(n) } })
			} else if (AUTOCOMPLETE_SINGLE_FILTERS.includes(key)) {
				var value = { id: parseInt(params[key]) }
			} else {
				var value = params[key]
			}

			return {
				...values,
				[key]: value,
			}
		}, {})

		return {
			categoriesEnabled,
			filterValues,
		}
	}

	formatValue(value, key) {
		if (isMoment(value)) {
			return value.format(DATE_FORMAT)
		} else if (AUTOCOMPLETE_MULTI_FILTERS.includes(key)) {
			return value.map(({ id }) => id).join(',')
		} else if (AUTOCOMPLETE_SINGLE_FILTERS.includes(key)) {
			if (!value) {
				return null
			}
			return value.id
		} else {
			return value
		}
	}

	getPageFetchParams() {
		const categoriesEnabledById = this.state.categoriesEnabled
			.filter(({ enabled }) => enabled)
			.map(({ id }) => id)

		const whitelistedFields = this.state.categoriesEnabled
			.filter(({ enabled }) => enabled)
			.reduce((list, category) => {
				const related_field_names = category.related_fields.map((field) => field.name)
				return list.concat(related_field_names)
			}, FilterSets['General'].fields)


		const filterValues = DATE_FILTERS.reduce((filters, date_field) => {
			const upper_date = date_field.replace('_lower', '_upper')
			const hasCompleteRange = (
				filters.hasOwnProperty(date_field) &&
				filters.hasOwnProperty(upper_date) &&
				upper_date !== date_field
			)
			const shouldSwap = (
				hasCompleteRange &&
				filters[date_field].isAfter(filters[upper_date])
			)
			if (shouldSwap) {
				return {
					...filters,
					[date_field]: filters[upper_date],
					[upper_date]: filters[date_field],
				}
			}

			return filters
		}, {...this.state.filterValues})

		const formattedFilterValues = Object.keys(filterValues)
			.reduce((values, key) => {
				const value = filterValues[key]
				return {
					...values,
					[key]: this.formatValue(value, key),
				}
			}, {})

		const params = {
			...queryString.parse(window.location.search),
			categories: categoriesEnabledById.join(','),
			...formattedFilterValues,
		}


		return Object.keys(params).reduce((obj, key) => {
			// Remove blank values from the query string.
			if (!params[key]) {
				return obj
			}
			// Remove fields of categories that are not enabled
			if (ALL_FILTERS.includes(key) && !whitelistedFields.includes(key)) {
				return obj
			}

			return {
				...obj,
				[key]: params[key]
			}
		}, {})
	}

	/**
	 * We want to redirect to a CategoryPage or IncidentIndexPage when the Apply
	 * Filters button is hit on a page that isn't of those types. This function
	 * determines which page should be redirected to based on the number of
	 * categories. If only one category is whitelisted, just redirect to that
	 * CategoryPage.
	 */
	getExternalUrl() {
		const categoriesEnabled = this.state.categoriesEnabled
			.filter(({ enabled }) => enabled)

		if (categoriesEnabled.length === 1) {
			return categoriesEnabled[0].url
		}

		return this.props.external
	}

	handleToggle() {
		this.setState({
			filtersExpanded: !this.state.filtersExpanded,
		})
	}

	handleSelection(id) {
		const categoriesEnabled = this.state.categoriesEnabled.map(category => {
			if (category.id !== id) {
				return category
			}

			return {
				...category,
				enabled: !category.enabled,
			}
		})

		const selectedAccordions = this.state.selectedAccordions.filter(_id => {
			if (_id === -1) {
				return true
			}
			return categoriesEnabled.some(category => category.enabled && category.id === _id)
		})

		this.setState({
			categoriesEnabled,
			selectedAccordions,
			filtersTouched: true,
		})
	}

	handlePopState() {
		this.setState(
			this.getStateFromQueryParams(),
			() => this.fetchPage(this.getPageFetchParams())
		)
	}

	handleApplyFilters(e) {
		e.preventDefault()

		const params = this.getPageFetchParams()

		const qs = '?' + queryString.stringify(params)
		if (this.props.applyExternally) {
			window.location = this.getExternalUrl() + qs
		} else {
			history.pushState(null, null, qs)
			this.fetchPage(params)
		}
	}

	handleClearFilters() {
		const currentParams = queryString.parse(window.location.search)
		const strippedParams = Object.keys(currentParams).reduce((params, key) => {
			if (ALL_FILTERS.includes(key)) {
				return params
			}

			if (key === 'categories') {
				return params
			}

			return {
				...params,
				[key]: currentParams[key],
			}
		}, {})


		const nextState = {
			filterValues: {},
			filtersTouched: false,
		}

		if (!this.props.noCategoryFiltering) {
			nextState.categoriesEnabled = this.state.categoriesEnabled.map(category => {
				return {
					...category,
					enabled: false,
				}
			})
		}

		this.setState(nextState)
		history.pushState(null, null, '?' + queryString.stringify(strippedParams))
		this.fetchPage(strippedParams)
	}

	fetchPage(params) {
		this.setState({
			loading: this.state.loading + 1,
			filtersTouched: false,
		})

		axios.get('?' + queryString.stringify(params))
			.then(
				response => {
					this.setState({
						loading: this.state.loading - 1,
					})

					if (response.status === 200) {
						if (!window._infiniteScroller) {
							console.warn('No InfiniteScroller instance found.')
							return
						}
						window._infiniteScroller.insertPageFromBody(
							response.data,
							{ replace: true }
						)
					}
				},

				() => {
					this.setState({
						loading: this.state.loading - 1,
					})
				}
			)
	}

	handleFilterChange(label, event) {
		console.log('label', label)
		console.log('event', event)
		let value
		if (!event) {
			value = null
		} else if (isMoment(event)) {
			value = event
		} else if (event.target && event.target.hasOwnProperty('checked')) {
			value = event.target.checked
		} else if (event.target) {
			value = event.target.value
		}

		const receivedErroneousValue = (
			!DATE_FILTERS.includes(label) &&
			!(event.target && event.target._autocomplete) &&
			(value === null || value === undefined)
		)
		if (receivedErroneousValue) {
			console.error("Erroneous Value", value)
			return
		}

		this.setState({
			filterValues: {
				...this.state.filterValues,
				[label]: value,
			},
			filtersTouched: true,
		})
	}

	handleAccordionSelection(id) {
		const { selectedAccordions } = this.state
		if (selectedAccordions.includes(id)) {
			this.setState({
				selectedAccordions: selectedAccordions.filter(_id => _id !== id)
			})
		} else {
			this.setState({
				selectedAccordions: this.state.selectedAccordions.concat(id)
			})
		}
	}

	render() {
		const {
			categoriesEnabled,
			filterValues,
			filtersExpanded,
			filtersTouched,
			selectedAccordions,
		} = this.state

		const {
			noCategoryFiltering,
			changeFiltersMessage,
			filterChoices,
			exportPath,
		} = this.props

		return (
			<div className="filters">
				<form onSubmit={this.handleApplyFilters}>
					<FiltersHeader
						filterValues={filterValues}
						filtersExpanded={filtersExpanded}
						categoriesEnabled={categoriesEnabled}
						handleToggle={this.handleToggle}
						changeFiltersMessage={changeFiltersMessage}
					/>

					<FiltersExpandable filtersExpanded={filtersExpanded}>
						{!noCategoryFiltering && (
							<FiltersCategorySelection
								categoriesEnabled={categoriesEnabled}
								handleSelection={this.handleSelection}
							/>
						)}

						<FiltersBody
							selectedAccordions={selectedAccordions}
							categoriesEnabled={categoriesEnabled}
							filterValues={filterValues}
							handleAccordionSelection={this.handleAccordionSelection}
							handleFilterChange={this.handleFilterChange}
							noCategoryFiltering={noCategoryFiltering}
							choices={filterChoices}
						/>

						<FiltersFooter
							handleClearFilters={this.handleClearFilters}
							pageFetchParams={this.getPageFetchParams()}
							loading={this.state.loading}
							filtersTouched={filtersTouched}
							exportPath={exportPath}
						/>
					</FiltersExpandable>
				</form>
			</div>
		)
	}
}


export default IncidentFiltering
