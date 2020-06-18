import React from 'react'
import PropTypes from 'prop-types'

import MiniIncident from './MiniIncident'

import '../sass/CategoryModule.sass'

export default class CategoryModule extends React.PureComponent {
	render() {
		const {
			category,
			tag,
			incidentsPerModule,
			incidents,
		} = this.props
		return (
			<article className={`category-module category-module--${category.color}`}>
				<div className="category-module__header">
					<h1 className={`category-module__title category-module__title--${category.color}`}>
						{category.category}
					</h1>
					<div className="category-module__stats">
						<strong>{category.total_incidents}</strong>{' '}
						{category.category_plural}{' '}
						{category.total_journalists ? (<span>{/* TODO: Make this a fragment when we're on React 16*/}
							affecting <strong>{category.total_journalists}</strong> journalists.
						</span>) : ''}
						<span
							className="category-module__methodology-link"
						>
							Methodology
						</span>
					</div>
				</div>
				<div className="category-module__items">
					{incidents.slice(0, incidentsPerModule).map(incident => (
						<MiniIncident key={incident.url} incident={incident} />
					))}
					{category.total_incidents > incidentsPerModule ? (
						<a
							href={`${category.url}?tags=${tag}`}
							className="category-module__action"
						>
							More Incidents
						</a>
					) : ''}
				</div>
			</article>
		)
	}
}

CategoryModule.propTypes = {
	category: PropTypes.object.isRequired,
	incidents: PropTypes.array.isRequired,
	incidentsPerModule: PropTypes.number
}
