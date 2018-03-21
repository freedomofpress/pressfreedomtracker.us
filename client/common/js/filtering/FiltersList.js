import React, { PureComponent } from 'react'
import moment from 'moment'
import {
	AUTOCOMPLETE_SINGLE_FILTERS,
	AUTOCOMPLETE_MULTI_FILTERS,
	DATE_FILTERS,
	HUMAN_DATE_FORMAT,
} from '~/filtering/constants'


class FiltersList extends PureComponent {
	renderFilterValue(filter, filterValues) {
		let title = filter.title
		let renderedValue = filterValues[filter.name]
		if (filter.type === 'date') {
			title = title.slice(0, -8)
			const lowerDate = filterValues[`${filter.name}_lower`]
			const upperDate = filterValues[`${filter.name}_upper`]

			if (upperDate && lowerDate) {
				title = `${title} between`
				renderedValue = `${moment(lowerDate).format(HUMAN_DATE_FORMAT)} – ${moment(upperDate).format(HUMAN_DATE_FORMAT)}`
			} else if (upperDate) {
				title = `${title} before`
				renderedValue = moment(upperDate).format(HUMAN_DATE_FORMAT)
			} else {
				title = `${title} since`
				renderedValue = moment(lowerDate).format(HUMAN_DATE_FORMAT)
			}
		} else if (filter.type === 'boolean') {
			renderedValue = filterValues[filter.name] ? 'yes' : 'no'
		} else if (filter.type === 'choice') {
			const selected = filter.choices.find(choice => choice[0] === filterValues[filter.name])
			if (selected) renderedValue = selected[1]
		} else if (filter.type === 'autocomplete') {
			if (Array.isArray(filterValues[filter.name])) {
				renderedValue = (
					<ul className="filters__summary-list">
						{filterValues[filter.name].map(({ label, id }) => (
							<li
								key={id}
								className="filters__summary-item"
							>
								{label}
							</li>
						))}
					</ul>
				)
			} else {
				renderedValue = filterValues[filter.name].label
			}
		}

		return (
			<span>
				<span className="filters__text--dim">{title}:</span>
				{' '}
				{renderedValue}
			</span>
		)
	}

	render() {
		const {
			categories,
			categoriesEnabled,
			filterValues,
		} = this.props

		const filters = categories.filter(({ id }) => categoriesEnabled[id]).reduce((acc, category) => {
			return [
				...acc,
				...category.filters.filter(filter => {
					if (filter.type === 'date') {
						return filterValues[`${filter.name}_lower`] || filterValues[`${filter.name}_upper`]
					} else {
						return filterValues[filter.name]
					}
				}),
			]
		}, [])

		return (
			<ul className="filters__summary-list">
				{filters.map(filter => (
					<li key={filter.name} className="filters__summary-item">
						{this.renderFilterValue(filter, filterValues)}
					</li>
				))}
			</ul>
		)
	}
}


export default FiltersList
