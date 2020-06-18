import React from 'react'
import PropTypes from 'prop-types'


export default class MiniIncident extends React.PureComponent {
	render() {
		const {
			incident,
		} = this.props
		return (
			<div className="incident__body-excerpt">
				<h3 className="incident__title">
					<a href={incident.url}>{incident.title}</a>
				</h3>
				<div className="incident__date">{incident.date}</div>
			</div>
		)
	}
}

MiniIncident.propTypes = {
	incident: PropTypes.object.isRequired,
}
