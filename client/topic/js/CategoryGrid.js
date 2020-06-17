import React from 'react'
import PropTypes from 'prop-types'

import CategoryModule from './CategoryModule'


export default class CategoryGrid extends React.PureComponent {
	constructor(props) {
		super(props)
		this.state = {
			incidents: [],
			loading: true
		}
	}

	componentDidMount() {
		this.fetchData()
	}

	async fetchData() {
		this.setState({ incidents, loading: true })
		const querystring = new URLSearchParams(this.props.dataUrlParams).toString()
		const incidents = await (await fetch(this.props.dataUrl)).json()
		this.setState({ incidents, loading: false })
		setInterval(this.fetchData.bind(this), 300000)
	}

	render() {
		if (this.state.loading) {
			return <div>Loading... 🐢</div>
		}
		return (
			<div className="grid-50 js-incident-loading-parent">
				{this.state.incidents.map((category, index) => {
					if (category.incidents.length) {
						return (<CategoryModule
							key={index}
							category={category}
							incidentsPerModule={this.props.incidentsPerModule}
							incidents={category.incidents} />)
					}
				})}
			</div>
		)
	}
}

CategoryGrid.propTypes = {
	dataUrl: PropTypes.string.isRequired,
	incidentsPerModule: PropTypes.number
}
