import React, { PureComponent } from 'react'


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


class IncidentFiltering extends PureComponent {
	constructor(props, ...args) {
		super(props, ...args)

		this.handleToggle = this.handleToggle.bind(this)

		this.state = {
			filtersEnabled: props.availableCategories.map(category => {
				return {
					...category,
					enabled: false,
				}
			}),

			filtersExpanded: false,

			filtersApplied: [],
		}
	}

	handleToggle() {
		this.setState({
			filtersExpanded: !this.state.filtersExpanded,
		})
	}

	render() {
		const {
			filtersApplied,
			filtersExpanded,
		} = this.state

		return (
			<Filters>
				<FiltersHeader
					filtersApplied={filtersApplied}
					filtersExpanded={filtersExpanded}
					handleToggle={this.handleToggle}
				/>
			</Filters>
		)
	}
}


export default IncidentFiltering
