import React from 'react'
import PropTypes from 'prop-types'
import { format, parseISO } from 'date-fns'

import '../sass/MiniIncident.sass'


export default class MiniIncident extends React.PureComponent {
	render() {
		const {
			incident,
		} = this.props
		return (
			<div className="mini-incident">
				<h3 className="mini-incident__title">
					<a className="mini-incident__title-link" href={incident.url}>{incident.title}</a>
				</h3>
				<div className="mini-incident__date">
					{format(parseISO(incident.date), 'LLLL d, yyyy')}
				</div>
			</div>
		)
	}
}

MiniIncident.propTypes = {
	incident: PropTypes.object.isRequired,
}
