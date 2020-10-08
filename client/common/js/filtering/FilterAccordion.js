import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { CollapseIcon, ExpandIcon } from '~/filtering/Icons'
import FilterSet from '~/filtering/FilterSet'


class FilterAccordion extends PureComponent {
	constructor(props) {
		super(props)

		this.toggleAccordion = this.toggleAccordion.bind(this)

		this.state = {
			expanded: props.startExpanded,
		}
	}

	toggleAccordion() {
		this.setState({
			expanded: !this.state.expanded,
		})
	}

	getAppliedFilterLength() {
		return this.props.category.filters.filter(({name}) => {
			return Object.keys(
				this.props.filterValues
			).filter((filterKey) => filterKey.startsWith(name)).length
		}).length
	}

	render() {
		const {
			expanded,
		} = this.state

		const {
			category,
			collapsible,
			handleFilterChange,
			filterValues,
		} = this.props

		if (!category.filters || !(category.filters.length > 0)) {
			// Don't bother rendering an accordion with no filters
			return null
		}

		return (
			<li
				className={classNames(
					'filters__accordion-category',
					{ 'filters__accordion-category--no-divider': !collapsible }
				)}
			>
				{collapsible && (
					<button
						className={classNames(
							'filters__accordion',
							{ 'filters__accordion--active': expanded }
						)}
						onClick={this.toggleAccordion}
						type="button"
					>
						{expanded ? <CollapseIcon /> : <ExpandIcon />}
						{category.title}
						{(!expanded && this.getAppliedFilterLength())  ? (
							<span className="filters__count">
								{this.getAppliedFilterLength()}
							</span>
						) : ''}
					</button>
				)}

				{expanded && (
					<FilterSet
						filters={category.filters}
						handleFilterChange={handleFilterChange}
						filterValues={filterValues}
					/>
				)}
			</li>
		)
	}
}


FilterAccordion.propTypes = {
	category: PropTypes.object.isRequired,
	collapsible: PropTypes.bool.isRequired,
	handleFilterChange: PropTypes.func.isRequired,
	filterValues: PropTypes.object.isRequired,
	startExpanded: PropTypes.bool.isRequired,
}


export default FilterAccordion
