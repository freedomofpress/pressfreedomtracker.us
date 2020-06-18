import React from 'react'
import PropTypes from 'prop-types'

import '../sass/Popover.sass'

export default class Popover extends React.Component{
	constructor(props) {
		super(props)
		this.state = {
			position: { top: 0, left: 0, height: 0, width: 0 },
		}
		this.calculateOffset = this.calculateOffset.bind(this)
	}

	componentDidMount() {
		this.calculateOffset()
	}

	componentWillReceiveProps(nextProps, nextState) {
		if(nextProps.show === true) this.calculateOffset()
	}

	calculateOffset() {
		const parent = this._wrapper.parentNode
		this.setState({
			position: {
				top: parent.offsetTop,
				left: parent.offsetLeft,
				width: parent.offsetWidth,
				height: parent.offsetHeight,
			}
		})
	}

	render () {
		const {
			position,
			orientation
		} = this.state

		let top = position.top + position.height + 10
		let left = window.innerWidth < 400 ? 10 : position.left + position.width / 2

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
