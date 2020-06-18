import React from 'react'
import PropTypes from 'prop-types'

import MiniIncident from './MiniIncident'


export default class CategoryModule extends React.PureComponent {
	render() {
		const {
			category,
			tag,
			incidentsPerModule,
			incidents,
		} = this.props
		return (
			<div className="grid-50__item js-incident-loading-item">
				<article className={`
					incident
					incident--${category.color}
					incident--teaser`}
				>
					<div className="incident__body">
						<p className={`category-list__item category-list__item--${category.color}`}>
							{category.category}
						</p>
						<p className="category__stats">
							{category.total_incidents} {category.category_plural} affecting {category.total_journalists} journalists.
							<span
							 className="methodology"
							 title={category.methodology}>
								{ ' Methodology '}
							</span>
						</p>
						{incidents.slice(0, incidentsPerModule).map((incident, key) => (
							<MiniIncident key={key} incident={incident} />
						))}
						{category.total_incidents > incidentsPerModule ? (
							<a
								href={`${category.url}?tags=${tag}`}
								className="button button--outline button--center js-incident-loading-next-link"
							>
								More Incidents
							</a>
						) : ''}
					</div>
				</article>
			</div>
		)
	}
}

CategoryModule.propTypes = {
	category: PropTypes.object.isRequired,
	incidents: PropTypes.array.isRequired,
	incidentsPerModule: PropTypes.number
}
