import React, { PureComponent } from 'react'
import axios from 'axios'
import classNames from 'classnames'
import DatePicker from 'react-datepicker'
import queryString from 'query-string'
import moment, { isMoment } from 'moment'


const HUMAN_DATE_FORMAT = 'MMM Do YYYY'


const DATE_FORMAT = 'YYYY-MM-DD'


function SettingsIcon() {
	return (
		<svg
			width="16"
			height="16"
			viewBox="0 0 16 16"
			xmlns="http://www.w3.org/2000/svg"
			className="filters__icon"
		>
			<path d="M4 7H3V2h1v5zm-1 7h1v-3H3v3zm5 0h1V8H8v6zm5 0h1v-2h-1v2zm1-12h-1v6h1V2zM9 2H8v2h1V2zM5 8H2c-.55 0-1 .45-1 1s.45 1 1 1h3c.55 0 1-.45 1-1s-.45-1-1-1zm5-3H7c-.55 0-1 .45-1 1s.45 1 1 1h3c.55 0 1-.45 1-1s-.45-1-1-1zm5 4h-3c-.55 0-1 .45-1 1s.45 1 1 1h3c.55 0 1-.45 1-1s-.45-1-1-1z" fill="currentColor" fillRule="evenodd"/>
		</svg>
	)
}


function ExpandIcon() {
	return (
		<svg width="12" height="16" viewBox="0 0 12 16" xmlns="http://www.w3.org/2000/svg">
			<title>Expand</title>
			<path d="M12 9H7v5H5V9H0V7h5V2h2v5h5" fill="currentColor" fillRule="evenodd"/>
		</svg>
	)
}


function CollapseIcon() {
	return (
		<svg width="8" height="16" viewBox="0 0 8 16" xmlns="http://www.w3.org/2000/svg">
		  <title>Collapse</title>
		  <path d="M0 7v2h8V7" fill="currentColor" fillRule="evenodd"/>
		</svg>
	)
}


function Filters({ children }) {
	return <div className="filters">{children}</div>
}


function CategoryList({ categories }) {
	return (
		<ul className="filters__summary-list">
			{categories.map(category => (
				<li key={category.id} className="filters__summary-item">
					{category.title}
				</li>
			))}
		</ul>
	)
}


class FiltersList extends PureComponent {
	renderValue(label, value) {
		if (IncidentFiltering.DATE_FILTERS.includes(label)) {
			var formattedValue = value.format(HUMAN_DATE_FORMAT)
		} else {
			var formattedValue = value
		}

		if (label === 'lower_date') {
			return (
				<span>
					<span className="filters__text--dim">since</span>
					{' '}
					{formattedValue}
				</span>
			)
		} else if (label === 'upper_date') {
			return (
				<span>
					<span className="filters__text--dim">before</span>
					{' '}
					{formattedValue}
				</span>
			)
		} else {
			return null
		}
	}

	render() {
		const { filterValues } = this.props

		return (
			<ul className="filters__summary-list">
				{Object.keys(filterValues).map(label => (
					<li key={label} className="filters__summary-item">
						{this.renderValue(label, filterValues[label])}
					</li>
				))}
			</ul>
		)
	}
}


class FilterSummary extends PureComponent {
	render() {
		const {
			filtersExpanded,
			filterValues,
			categoriesEnabled,
			changeFiltersMessage,
		} = this.props

		const hasAnyFilters = (
			Object.keys(filterValues).length > 0 ||
			categoriesEnabled.some(category => {
				// Check if a non-General category has been whitelisted.
				return category.id !== -1 && category.enabled
			})
		)

		if (!hasAnyFilters) {
			return (
				<div className="filters__summary filters__text--dim">
					{changeFiltersMessage || 'No filters applied.'}
				</div>
			)
		}

		if (filtersExpanded) {
			return (
				<div className="filters__summary">
					Filters
				</div>
			)
		}

		const categories = categoriesEnabled.filter(({ enabled }) => enabled)
		const hasFilters = Object.keys(filterValues).length > 0

		return (
			<div className="filters__summary filters__summary--can-compact filters__text--dim">
				Showing <CategoryList categories={categories} />
				{hasFilters && ' '}
				{hasFilters && <FiltersList filterValues={filterValues} />}
			</div>
		)
	}
}


class FiltersHeader extends PureComponent {
	render() {
		const {
			filtersExpanded,
			filterValues,
			handleToggle,
			categoriesEnabled,
			changeFiltersMessage,
		} = this.props


		return (
			<div className="filters__header">
				<FilterSummary
					filtersExpanded={filtersExpanded}
					filterValues={filterValues}
					categoriesEnabled={categoriesEnabled}
					changeFiltersMessage={changeFiltersMessage}
				/>

				<button
					className="filters__button filters__button--no-shrink"
					onClick={handleToggle}
				>
					<SettingsIcon />

					{filtersExpanded ? 'Collapse Filters' : 'Change Filters'}
				</button>
			</div>
		)
	}
}


function FiltersExpandable({ filtersExpanded, children }) {
	return (
		<div className={classNames(
			'filters__expandable',
			{ 'filters__expandable--expanded': filtersExpanded }
		)}>
			{children}
		</div>
	)
}


class FiltersCategorySelection extends PureComponent {
	render() {
		const {
			categoriesEnabled,
			handleSelection,
		} = this.props

		return (
			<div className="filters__category-selection">
				<div className="filters__text">
					Limit to
				</div>

				<ul className="filters__categories">
					{categoriesEnabled.map(category => (
						<li
							key={category.id}
							className={classNames(
								'filters__category',
								{ 'filters__category--active': category.enabled }
							)}
							onClick={handleSelection.bind(null, category.id)}
						>
							{category.title}
						</li>
					))}
				</ul>
			</div>
		)
	}
}


function FilterSet({ children }) {
	return (
		<div className="filters__set">
			{children}
		</div>
	)
}


const FilterSets = {}


FilterSets['General'] = function({
	handleFilterChange,
	filterValues,
}) {
	return (
		<FilterSet>
			<div>
				Took place between
				{' '}
				<span className="filters__date-picker">
					<DatePicker
						onChange={handleFilterChange.bind(null, 'lower_date')}
						selected={filterValues.lower_date || ''}
						isClearable={true}
					/>
				</span>
				{' '}
				and
				{' '}
				<span className="filters__date-picker">
					<DatePicker
						onChange={handleFilterChange.bind(null, 'upper_date')}
						selected={filterValues.upper_date || ''}
						isClearable={true}
					/>
				</span>
			</div>
		</FilterSet>
	)
}


FilterSets['Equipment Search, Seizure, or Damage'] = function() {
	return (
		<FilterSet>
			No filters.
		</FilterSet>
	)
}


function FilterAccordion({
	category,
	selectedAccordions,
	handleAccordionSelection,
	handleFilterChange,
	filterValues,
	noCategoryFiltering
}) {
	if (!category.enabled) {
		return null
	}

	const FilterSet = typeof FilterSets[category.title] === 'function' ? FilterSets[category.title] : () => null
	const isActive = selectedAccordions.includes(category.id)
	const collapsible = !noCategoryFiltering

	return (
		<li
			className={classNames(
				'filters__accordion-category',
				{ 'filters__accordion-category--no-divider': noCategoryFiltering }
			)}
		>
			{collapsible && (
				<button
					className={classNames(
						'filters__accordion',
						{ 'filters__accordion--active': isActive }
					)}
					onClick={handleAccordionSelection.bind(null, category.id)}
				>
					{isActive ? <CollapseIcon /> : <ExpandIcon />}
					{category.title}
				</button>
			)}

			{isActive && (
				<FilterSet
					handleFilterChange={handleFilterChange}
					filterValues={filterValues}
				/>
			)}
		</li>
	)
}


class FiltersBody extends PureComponent {
	render() {
		const {
			selectedAccordions,
			handleAccordionSelection,
			categoriesEnabled,
			handleFilterChange,
			filterValues,
			noCategoryFiltering,
		} = this.props

		return (
			<ul className="filters__body">
				<FilterAccordion
					category={{
						id: -1,
						title: 'General',
						enabled: true,
					}}
					handleAccordionSelection={handleAccordionSelection}
					handleFilterChange={handleFilterChange}
					selectedAccordions={selectedAccordions}
					filterValues={filterValues}
					noCategoryFiltering={noCategoryFiltering}
				/>

				{categoriesEnabled.map(category => (
					<FilterAccordion
						key={category.id}
						category={category}
						handleAccordionSelection={handleAccordionSelection}
						selectedAccordions={selectedAccordions}
						filterValues={filterValues}
						noCategoryFiltering={noCategoryFiltering}
					/>
				))}
			</ul>
		)
	}
}


function HorizontalLoader() {
	return (
		<div className="horizontal-loader">
			<span className="horizontal-loader__circle"></span>
			<span className="horizontal-loader__circle"></span>
			<span className="horizontal-loader__circle"></span>
		</div>
	)
}


function FiltersFooter({
	handleApplyFilters,
	handleClearFilters,
	loading,
}) {
	return (
		<div className="filters__footer">
			<div className="filters__text filters__text--dim filters__text--meta">
				Need to do more complex filtering?
				{' '}
				<a href="#" className="filters__link">Download the Data.</a>
			</div>

			<span className="filters__button-toolbar">
				<button
					className="filters__button"
					onClick={handleClearFilters}
				>
					Clear Filters
				</button>

				<button
					className="filters__button filters__button--bordered filters__button--wide"
					onClick={handleApplyFilters}
				>
					{loading > 0 && <HorizontalLoader />}
					{loading === 0 && 'Apply Filters'}
				</button>
			</span>
		</div>
	)
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
			if (!IncidentFiltering.ALL_FILTERS.includes(key)) {
				return values
			}

			if (IncidentFiltering.DATE_FILTERS.includes(key)) {
				var value = moment(params[key])
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

	getPageFetchParams() {
		const categoriesEnabledById = this.state.categoriesEnabled
			.filter(({ enabled }) => enabled)
			.map(({ id }) => id)

		const filterValues = Object.keys(this.state.filterValues)
			.reduce((values, key) => {
				const value = this.state.filterValues[key]
				return {
					...values,
					[key]: isMoment(value) ? value.format(DATE_FORMAT) : value,
				}
			}, {})

		const params = {
			...queryString.parse(window.location.search),
			categories: categoriesEnabledById.join(','),
			...filterValues,
		}

		return Object.keys(params).reduce((obj, key) => {
			// Remove blank values from the query string.
			if (!params[key]) {
				return obj
			}

			return {
				...obj,
				[key]: params[key]
			}
		}, {})
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
		})
	}

	handlePopState() {
		this.setState(
			this.getStateFromQueryParams(),
			() => this.fetchPage(this.getPageFetchParams())
		)
	}

	handleApplyFilters() {
		const params = this.getPageFetchParams()
		const qs = '?' + queryString.stringify(params)
		if (this.props.applyExternally) {
			window.location = this.props.external + qs
		} else {
			history.pushState(null, null, qs)
			this.fetchPage(params)
		}
	}

	handleClearFilters() {
		const currentParams = queryString.parse(window.location.search)
		const strippedParams = Object.keys(currentParams).reduce((params, key) => {
			if (IncidentFiltering.ALL_FILTERS.includes(key)) {
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

		this.setState({
			categoriesEnabled: this.state.categoriesEnabled.map(category => {
				return {
					...category,
					enabled: false,
				}
			}),
			filterValues: {},
		})

		history.pushState(null, null, '?' + queryString.stringify(strippedParams))
		this.fetchPage(strippedParams)
	}

	fetchPage(params) {
		this.setState({
			loading: this.state.loading + 1,
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
		if (!event) {
			var value = null
		} else if (isMoment(event)) {
			var value = event
		} else {
			var value = event.target.value
		}

		if (event && !value) {
			return
		}

		this.setState({
			filterValues: {
				...this.state.filterValues,
				[label]: value,
			}
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
			selectedAccordions,
		} = this.state

		const {
			noCategoryFiltering,
			changeFiltersMessage,
		} = this.props

		return (
			<Filters>
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
					/>

					<FiltersFooter
						handleApplyFilters={this.handleApplyFilters}
						handleClearFilters={this.handleClearFilters}
						loading={this.state.loading}
					/>
				</FiltersExpandable>
			</Filters>
		)
	}
}


IncidentFiltering.ALL_FILTERS = [
	'lower_date',
	'upper_date',
]


IncidentFiltering.DATE_FILTERS = [
	'lower_date',
	'upper_date',
]


export default IncidentFiltering
