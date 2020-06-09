import React from 'react'
import PropTypes from 'prop-types'


export default class CategoryGrid extends React.PureComponent {
	constructor(props) {
		super(props)
		this.state = {
			incidents: [],
			loading: true,
		}
	}

	componentDidMount() {
		this.fetchData()
	}

	async fetchData() {
		this.setState({ incidents, loading: true })
		const querystring = new URLSearchParams(this.props.dataUrlParams).toString()
		const incidents = await (await fetch(`${this.props.dataUrl}?${querystring}`)).json()
		this.setState({ incidents, loading: false })
	}

	render() {
		return <div>{this.state.loading ? 'Loading... 🐢' : 'Loaded 🎉'}</div>
	}
}

CategoryGrid.propTypes = {
	dataUrl: PropTypes.string.isRequired,
	dataUrlParams: PropTypes.object.isRequired,
}
