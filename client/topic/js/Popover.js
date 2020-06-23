import React from 'react'
import PropTypes from 'prop-types'

import '../sass/Popover.sass'

export default class Popover extends React.Component{
	_calculateOffset() {
		// If there is no set wrapper element (probably first render)
		// return zeroes for all parameters
		if (!this._wrapper) return { top: 0, left: 0, width: 0, height: 0 }

		// Otherwise calculate the offset criteria
		const parent = this._wrapper.parentNode
		return {
			top: parent.offsetTop,
			left: parent.offsetLeft,
			width: parent.offsetWidth,
			height: parent.offsetHeight,
		}
	}

	render() {
		const position = this._calculateOffset()
		const top = position.top + position.height + 10
		const left = window.innerWidth < 400 ? 10 : position.left + position.width / 2
		return (
			<div
				className={`popover ${this.props.show && 'popover--visible'}`}
				style={{ top, left }}
				ref={c => this._wrapper = c}
			>
				{this.props.children}
			</div>
		)
	}
}

Popover.propTypes = {
	children: PropTypes.node.isRequired,
	show: PropTypes.bool,
}

Popover.defaultProps = {
	show: false,
}
