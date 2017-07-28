import React, { PureComponent } from 'react'
import {
	AUTOCOMPLETE_SINGLE_FILTERS,
	AUTOCOMPLETE_MULTI_FILTERS,
	DATE_FILTERS,
	HUMAN_DATE_FORMAT,
} from '~/filtering/constants'


class FiltersList extends PureComponent {
	renderValue(label, value) {
		if (DATE_FILTERS.includes(label)) {
			var formattedValue = value.format(HUMAN_DATE_FORMAT)
		} else {
			var formattedValue = value
		}

		const underscoreRe = /_/g

		if (DATE_FILTERS.includes(label)) {
			const period = label.includes('_lower') ? 'since' : 'before'
			const description = label.substring(0, label.length - 6).replace(underscoreRe, ' ')
			return (
				<span>
					<span className="filters__text--dim">{description} {period}</span>
					{' '}
					{formattedValue}
				</span>
			)
		} else if (AUTOCOMPLETE_MULTI_FILTERS.includes(label)) {
			const description = label.replace(underscoreRe, ' ')
			return (
				<span>
					<span className="filters__text--dim">{description}:</span>
					{' '}
					<ul className="filters__summary-list">
						{value.map(({ label, id }) => (
							<li
								key={id}
								className="filters__summary-item"
							>
								{label}
							</li>
						))}
					</ul>
				</span>
			)
		} else if (AUTOCOMPLETE_SINGLE_FILTERS.includes(label)) {
			const description = label.replace(underscoreRe, ' ')
			return (
				<span>
					<span className="filters__text--dim">{description}:</span>
					{' '}
					{value.label}
				</span>
			)
		} else {
			const description = label.replace(underscoreRe, ' ')
			return (
				<span>
					<span className="filters__text--dim">{description}:</span>
					{' '}
					{formattedValue}
				</span>
			)
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


export default FiltersList
