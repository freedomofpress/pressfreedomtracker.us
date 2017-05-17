import React, { PureComponent } from 'react'
import { render } from 'react-dom'
import axios from 'axios'


axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


class Autocomplete extends PureComponent {
	constructor(props, ...args) {
		super(props, ...args)

		this.handleChange = this.handleChange.bind(this)

		this.state = {
			value: props.value,
			input: {
				value: '',
			},
			suggestions: [],
		}
	}

	handleChange(event) {
		const { value } = event.target
		this.checkNewSuggestions(value)
		this.setState({
			input: {
				...this.state.input,
				value,
			}
		})
	}

	checkNewSuggestions(value) {
		if (value === this.state.value) {
			return
		}

		const params = {
			query: value,
			type: this.props.type,
		}
		axios.get('/autocomplete/search/', { params })
			.then(res => {
				if (res.status !== 200) {
					return
				}

				this.setState({
					suggestions: res.data.pages
				})
			})
	}

	handleClick(suggestion) {
		this.setState({
			value: this.state.value.concat(suggestion),
		})
	}

	render() {
		const { name } = this.props
		const { value, input } = this.state

		const suggestions = this.state.suggestions.filter(suggestion => {
			return value.every(({ id }) => id !== suggestion.id)
		})

		return (
			<span>
				<input
					type="hidden"
					value={JSON.stringify(value)}
					name={name}
				/>

				<input
					type="text"
					onChange={this.handleChange}
					{...input}
				/>

				<ul>
					{suggestions.map(suggestion =>
						<li
							key={suggestion.id}
							onClick={this.handleClick.bind(this, suggestion)}
						>
							{suggestion.label}
						</li>
					)}
				</ul>

				{value.map(page =>
					<div key={page.id}>{page.label}</div>
				)}
			</span>
		)
	}
}


window.renderAutocompleteWidget = (id, name, value, type) => {
	render(
		<Autocomplete
			name={name}
			value={value}
			type={type}
		/>,
		document.getElementById(id)
	)
}
