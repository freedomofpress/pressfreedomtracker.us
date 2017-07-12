import React, { PureComponent } from 'react'
import axios from 'axios'
import classNames from 'classnames'
import queryString from 'query-string'


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


function Filters({ children }) {
	return <div className="filters">{children}</div>
}


class FiltersHeader extends PureComponent {
	render() {
		const {
			filtersExpanded,
			filterValues,
			handleToggle
		} = this.props


		const hasAnyFilters = Object.keys(filterValues).length > 0
		return (
			<div className="filters__header">
				{!hasAnyFilters && (
					<div className="filters__text filters__text--dim">
						No filters applied.
					</div>
				)}

				{hasAnyFilters && (
					<div className="filters__text">
						Filters
					</div>
				)}

				<button
					className="filters__button"
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
					Include
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
				<input
					type="date"
					onChange={handleFilterChange.bind(null, 'lower_date')}
					value={filterValues.lower_date || ''}
				/>
				{' '}
				and
				{' '}
				<input
					type="date"
					onChange={handleFilterChange.bind(null, 'upper_date')}
					value={filterValues.upper_date || ''}
				/>
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
	selectedAccordion,
	handleAccordionSelection,
	handleFilterChange,
	filterValues,
}) {
	if (!category.enabled) {
		return null
	}

	const FilterSet = typeof FilterSets[category.title] === 'function' ? FilterSets[category.title] : () => null
	const isActive = category.id === selectedAccordion

	return (
		<li>
			<button
				className={classNames(
					'filters__accordion',
					{ 'filters__accordion--active': isActive }
				)}
				onClick={handleAccordionSelection.bind(null, category.id)}
			>
				{category.title}
			</button>

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
			selectedAccordion,
			handleAccordionSelection,
			categoriesEnabled,
			handleFilterChange,
			filterValues,
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
					selectedAccordion={selectedAccordion}
					filterValues={filterValues}
				/>

				{categoriesEnabled.map(category => (
					<FilterAccordion
						key={category.id}
						category={category}
						handleAccordionSelection={handleAccordionSelection}
						selectedAccordion={selectedAccordion}
						filterValues={filterValues}
					/>
				))}
			</ul>
		)
	}
}


function FiltersFooter({ handleApplyFilters }) {
	return (
		<div className="filters__footer">
			<div className="filters__text filters__text--dim filters__text--meta">
				Need to do more complex filtering?
				{' '}
				<a href="#" className="filters__link">Download the Data.</a>
			</div>

			<button
				className="filters__button filters__button--bordered filters__button--wide"
				onClick={handleApplyFilters}
			>
				Apply Filters
			</button>
		</div>
	)
}


class IncidentFiltering extends PureComponent {
	constructor(props, ...args) {
		super(props, ...args)

		this.handleToggle = this.handleToggle.bind(this)
		this.handleSelection = this.handleSelection.bind(this)
		this.handleApplyFilters = this.handleApplyFilters.bind(this)
		this.handleAccordionSelection = this.handleAccordionSelection.bind(this)
		this.handleFilterChange = this.handleFilterChange.bind(this)

		const params = queryString.parse(location.search)
		const categoriesEnabledById = (params.categories || '').split(',').map(n => parseInt(n))
		const filterValues = Object.keys(params).reduce((values, key) => {
			if (IncidentFiltering.ALL_FILTERS.includes(key)) {
				return {
					...values,
					[key]: params[key],
				}
			}

			return values
		}, {})

		this.state = {
			categoriesEnabled: props.availableCategories.map(category => {
				return {
					...category,
					enabled: categoriesEnabledById.includes(category.id),
				}
			}),

			filtersExpanded: false,

			filterValues,

			selectedAccordion: -1,
		}
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

		const isSelectedAccordionIsEnabled = categoriesEnabled.some(category => {
			return category.enabled && this.state.selectedAccordion === category.id
		})

		this.setState({
			categoriesEnabled,
			selectedAccordion: isSelectedAccordionIsEnabled ? this.state.selectedAccordion : -1,
		})
	}

	handleApplyFilters() {
		const categoriesEnabledById = this.state.categoriesEnabled
			.filter(({ enabled }) => enabled)
			.map(({ id }) => id)

		const params = {
			...queryString.parse(window.location.search),
			categories: categoriesEnabledById.join(','),
			...this.state.filterValues,
		}

		if (categoriesEnabledById.length === 0) {
			// Remove blank ?categories= value.
			delete params.categories
		}

		history.pushState(null, null, '?' + queryString.stringify(params))

		axios.get('?' + queryString.stringify(params))
			.then(response => {
				if (response.status === 200) {
					this.handlePageLoad(response.data)
				}
			})
	}

	handlePageLoad(ajaxBodyHtml) {
		const containerElm = document.querySelector('.incident-grid')
		if (!containerElm) {
			console.warn('No .incident-grid exists in the current DOM structure.')
			return
		}

		const tempContainerElm = document.createElement('span')
		tempContainerElm.innerHTML = ajaxBodyHtml
		const newContainerElm = tempContainerElm.querySelector('.incident-grid')
		if (!newContainerElm) {
			console.warn('No .incident-grid exists in the newly fetched DOM structure.')
			return
		}
		containerElm.parentNode.replaceChild(newContainerElm, containerElm)
	}

	handleFilterChange(label, event) {
		const value = event.target.value
		if (!value) {
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
		this.setState({ selectedAccordion: id })
	}

	render() {
		const {
			categoriesEnabled,
			filterValues,
			filtersExpanded,
			selectedAccordion,
		} = this.state

		return (
			<Filters>
				<FiltersHeader
					filterValues={filterValues}
					filtersExpanded={filtersExpanded}
					handleToggle={this.handleToggle}
				/>

				<FiltersExpandable filtersExpanded={filtersExpanded}>
					<FiltersCategorySelection
						categoriesEnabled={categoriesEnabled}
						handleSelection={this.handleSelection}
					/>

					<FiltersBody
						selectedAccordion={selectedAccordion}
						categoriesEnabled={categoriesEnabled}
						filterValues={filterValues}
						handleAccordionSelection={this.handleAccordionSelection}
						handleFilterChange={this.handleFilterChange}
					/>

					<FiltersFooter
						handleApplyFilters={this.handleApplyFilters}
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


export default IncidentFiltering
