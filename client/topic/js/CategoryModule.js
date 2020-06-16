import React from 'react'
import PropTypes from 'prop-types'

import MiniIncident from './MiniIncident'


export default class CategoryModule extends React.PureComponent {
	render() {
        const {
			category,
			incidents,
        } = this.props
        console.log(incidents)
		return (
            <div className="grid-50__item js-incident-loading-item">
                <article className="
                    incident
                    incident--gamboge
                    incident--teaser"
                >
                    <div className="incident__body">
                        <p className="category-list__item category-list__item--gamboge">
                            {category}
                        </p>
                        {incidents.slice(0, 4).map(incident => (
                            <MiniIncident incident={incident} />
                        ))}
                    </div>
                </article>
            </div>
        )
	}
}

CategoryModule.propTypes = {
	category: PropTypes.string.isRequired,
	incidents: PropTypes.array.isRequired,
}
