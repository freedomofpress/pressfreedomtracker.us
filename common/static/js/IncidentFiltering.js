import React, { PureComponent } from 'react'


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
