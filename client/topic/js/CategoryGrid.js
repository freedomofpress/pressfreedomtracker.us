import React from 'react'
import PropTypes from 'prop-types'

import CategoryModule from './CategoryModule'


export default class CategoryGrid extends React.PureComponent {
	constructor(props) {
		super(props)
		this.state = {
			incidents: [],
			loading: true,
			categories: []
		}
	}

	componentDidMount() {
		this.fetchData()
	}

	async fetchData() {
		this.setState({ incidents, loading: true, categories })
		const querystring = new URLSearchParams(this.props.dataUrlParams).toString()
		const incidents = await (await fetch(`${this.props.dataUrl}?${querystring}`)).json()
		incidents.forEach(incident => {
			incident['category'] = incident['categories'].split(',')[0]
		});
		const categories = [...new Set(incidents.map(incident => incident.category))];
		console.log(categories)
		this.setState({ incidents, loading: false, categories })
	}

	render() {
		if (this.state.loading) {
			return <div>Loading... 🐢</div>
		}
		return (
			<div className="grid-50 js-incident-loading-parent">
				{this.state.categories.map(category => {
					const categoryIncidents = this.state.incidents.filter( incident => 
						incident['category'] == category
					)
					console.log(categoryIncidents)
					return (<CategoryModule
						category={category}
						incidents={categoryIncidents} />)
				})}
			</div>
		)
	}
}

CategoryGrid.propTypes = {
	dataUrl: PropTypes.string.isRequired,
	dataUrlParams: PropTypes.object.isRequired,
}
