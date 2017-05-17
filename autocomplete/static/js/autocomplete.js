import React, { PureComponent } from 'react'
import { render } from 'react-dom'
import axios from 'axios'


axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


class Autocomplete extends PureComponent {
	constructor(props, ...args) {
		super(props, ...args)

		this.handleChange = this.handleChange.bind(this)
		this.handleCreate = this.handleCreate.bind(this)

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
			exclude: this.props.value.map(({ id }) => id).join(','),
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

	handleRemove(page) {
		this.setState({
			value: this.state.value.filter(({ id }) => id !== page.id)
		})
	}

	handleCreate() {
		const { value } = this.state.input
		if (value.trim() === '') {
			return
		}

		const data = new FormData()
		data.set('type', this.props.type)
		data.set('value', value)
		axios.post('/autocomplete/create/', data)
			.then(res => {
				if (res.status !== 200) {
					this.setState({ isLoading: false })
					return
				}

				this.setState({
					isLoading: false,
					value: this.state.value.concat(res.data),
				})
			})
		this.setState({ isLoading: true })
	}

	render() {
		const { name } = this.props
		const { value, input } = this.state

		const suggestions = this.state.suggestions.filter(suggestion => {
			return value.every(({ id }) => id !== suggestion.id)
		})

		const canCreate = this.props.canCreate && input.value.trim() !== ''

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

				<h3>Search</h3>
				<ul>
					{suggestions.map(suggestion =>
						<li
							key={suggestion.id}
							onClick={this.handleClick.bind(this, suggestion)}
						>
							{suggestion.label}
						</li>
					)}

					{canCreate && (
						<li
							key="create"
							onClick={this.handleCreate}
						>
							Create new “{input.value}”
						</li>
					)}
				</ul>

				<h3>Selected</h3>
				{value.map(page =>
					<div key={page.id}>
						{page.label}

						<button
							type="button"
							onClick={this.handleRemove.bind(this, page)}
						>
							Remove
						</button>
					</div>
				)}
			</span>
		)
	}
}


window.renderAutocompleteWidget = (id, name, value, type, canCreate) => {
	render(
		<Autocomplete
			name={name}
			value={value}
			type={type}
			canCreate={canCreate}
		/>,
		document.getElementById(id)
	)
}
