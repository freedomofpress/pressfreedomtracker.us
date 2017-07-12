import React, { PureComponent } from 'react'
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
			filtersApplied,
			handleToggle
		} = this.props

		return (
			<div className="filters__header">
				{filtersApplied.length === 0 && (
					<div className="filters__text filters__text--dim">
						No filters applied.
					</div>
				)}

				{filtersApplied.length > 0 && (
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


FilterSets['General'] = () => {
	return (
		<FilterSet>
			hello
		</FilterSet>
	)
}


FilterSets['Equipment Search, Seizure, or Damage'] = () => {
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

			{isActive && <FilterSet />}
		</li>
	)
}


class FiltersBody extends PureComponent {
	render() {
		const {
			selectedAccordion,
			handleAccordionSelection,
			categoriesEnabled,
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
					selectedAccordion={selectedAccordion}
				/>

				{categoriesEnabled.map(category => (
					<FilterAccordion
						key={category.id}
						category={category}
						handleAccordionSelection={handleAccordionSelection}
						selectedAccordion={selectedAccordion}
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

		const params = queryString.parse(location.search)
		const categoriesEnabledById = (params.categories__enabled || '').split(',').map(n => parseInt(n))

		this.state = {
			categoriesEnabled: props.availableCategories.map(category => {
				return {
					...category,
					enabled: categoriesEnabledById.includes(category.id),
				}
			}),

			filtersExpanded: false,

			filtersApplied: [],

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
			categories__enabled: categoriesEnabledById.join(','),
		}

		history.pushState(null, null, '?' + queryString.stringify(params))
	}

	handleAccordionSelection(id) {
		this.setState({ selectedAccordion: id })
	}

	render() {
		const {
			categoriesEnabled,
			filtersApplied,
			filtersExpanded,
			selectedAccordion,
		} = this.state

		return (
			<Filters>
				<FiltersHeader
					filtersApplied={filtersApplied}
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
						filtersApplied={filtersApplied}
						handleAccordionSelection={this.handleAccordionSelection}
					/>

					<FiltersFooter
						handleApplyFilters={this.handleApplyFilters}
					/>
				</FiltersExpandable>
			</Filters>
		)
	}
}


export default IncidentFiltering
