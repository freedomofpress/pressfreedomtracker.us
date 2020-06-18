import React from 'react'
import PropTypes from 'prop-types'

import CategoryModule from './CategoryModule'


export default class CategoryGrid extends React.PureComponent {
	constructor(props) {
		super(props)


		// Start with initial data if it exists
		const initialDataEl = document.getElementById('js-topic-grid-initial-data')

		this.state = {
			incidents: initialDataEl ? JSON.parse(initialDataEl.textContent) : [],
			loading: !initialDataEl,
		}

		this.fetchData = this.fetchData.bind(this)
	}

	componentDidMount() {
		// Kick off asynchronous fetching
		// If we didn't preseed any data, kick it off immediately. Otherwise wait
		// five minutes to update
		if(this.state.incidents.length === 0 && loading === true) {
			this.fetchData()
		} else {
			setTimeout(this.fetchData.bind(this), 5 * 60 * 1000)
		}
	}

	async fetchData() {
		this.setState({ incidents, loading: true })
		const querystring = new URLSearchParams(this.props.dataUrlParams).toString()
		const incidents = await (await fetch(this.props.dataUrl)).json()
		this.setState({ incidents, loading: false })
		setTimeout(this.fetchData, 5 * 60 * 1000)
	}

	render() {
		if (this.state.incidents.length === 0 && loading === true) {
			// This should never really be shown as long as we seed with initial data
			return <div>Loading...</div>
		}
		return (
			<div className="grid-50">
				{this.state.incidents.map((category, index) => {
					if (category.incidents.length) {
						return (
							<div className="grid-50__item" key={index}>
								<CategoryModule
									category={category}
									tag={this.props.tag}
									incidentsPerModule={this.props.incidentsPerModule}
									incidents={category.incidents}
								/>
							</div>
						)
					}
				})}
			</div>
		)
	}
}

CategoryGrid.propTypes = {
	dataUrl: PropTypes.string.isRequired,
	incidentsPerModule: PropTypes.number,
	tag: PropTypes.number
}
