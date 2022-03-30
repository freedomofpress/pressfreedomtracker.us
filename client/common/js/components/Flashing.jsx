import React from 'react'
import PropTypes from 'prop-types'

import './Flashing.sass'

export default function Flashing({ flashing = true, children }) {
	return <div className={flashing ? 'flashing' : 'flashing flashing--off'}>{children}</div>
}

Flashing.propTypes = {
	flashing: PropTypes.bool,
	children: PropTypes.node.isRequired,
}
