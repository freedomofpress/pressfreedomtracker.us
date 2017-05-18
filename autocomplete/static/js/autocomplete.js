import React, { PureComponent } from 'react'
import { render } from 'react-dom'
import PropTypes from 'prop-types'
import axios from 'axios'


axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


class Suggestions extends PureComponent {
	render() {
		const {
			suggestions,
			canCreate,
			onClick,
			onCreate,
			input,
		} = this.props

		return (
			<ul>
				{suggestions.map(suggestion =>
					<li
						key={suggestion.id}
						onClick={onClick.bind(null, suggestion)}
					>
						{suggestion.label}
					</li>
				)}

				{canCreate && (
					<li
						key="create"
						onClick={onCreate}
					>
						Create new “{input.value}”
					</li>
				)}
			</ul>
		)
	}
}


class Single extends PureComponent {
	render() {
		const {
			selected,
			onChange,
			onClick,
			onCreate,
			input,
			canCreate,
		} = this.props

		if (selected) {
			return (
				<span>
					{selected.label}

					<button
						type="button"
						onClick={onClick.bind(null, null)}
					>
						Remove
					</button>
				</span>
			)
		}

		const suggestions = this.props.suggestions.filter(suggestion => {
			if (!selected) {
				return true
			}
			return suggestion.id !== selected.id
		})

		return (
			<span>
				<input
					type="text"
					onChange={onChange}
					{...input}
				/>

				<Suggestions
					suggestions={suggestions}
					onClick={onClick}
					onCreate={onCreate}
					canCreate={canCreate}
					input={input}
				/>
			</span>
		)
	}
}


class Multi extends PureComponent {
	constructor(...args) {
		super(...args)

		this.handleClick = this.handleClick.bind(this)
	}

	handleClick(suggestion) {
		const { onClick, selections } = this.props
		onClick(selections.concat(suggestion))
	}

	handleRemove(page) {
		const { onClick, selections } = this.props
		onClick(selections.filter(({ id }) => id !== page.id))
	}

	render() {
		const {
			selections,
			onChange,
			onCreate,
			canCreate,
			input,
		} = this.props

		const suggestions = this.props.suggestions.filter(suggestion => {
			if (!selections) {
				return true
			}
			return selections.every(({ id }) => id !== suggestion.id)
		})

		return (
			<span>
				<h3>Search</h3>
				<input
					type="text"
					onChange={onChange}
					{...input}
				/>

				<Suggestions
					suggestions={suggestions}
					onClick={this.handleClick}
					onCreate={onCreate}
					canCreate={canCreate}
					input={input}
				/>

				<h3>Selected</h3>
				{selections.length === 0 && (
					<span>Nothing selected.</span>
				)}
				{selections.map(selection =>
					<div key={selection.id}>
						{selection.label}

						<button
							type="button"
							onClick={this.handleRemove.bind(this, selection)}
						>
							Remove
						</button>
					</div>
				)}
			</span>
		)
	}
}


Multi.defaultProps = {
	selections: [],
}


class Autocomplete extends PureComponent {
	constructor(props, ...args) {
		super(props, ...args)

		this.handleClick = this.handleClick.bind(this)
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

	getExclusions() {
		const { value } = this.state
		if (!value) {
			return ''
		}

		if (this.props.isSingle && value) {
			return value.id
		}

		return value.map(({ id }) => id).join(',')
	}

	checkNewSuggestions(value) {
		if (value === this.state.value) {
			return
		}

		const params = {
			query: value,
			type: this.props.type,
			exclude: this.getExclusions(),
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

	handleClick(value) {
		this.setState({ value })
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

				const value = this.props.isSingle ? res.data : this.state.value.concat(res.data)

				this.setState({
					isLoading: false,
					value,
				})
			})
		this.setState({ isLoading: true })
	}

	render() {
		const { name, isSingle } = this.props
		const { value, input, suggestions } = this.state

		const canCreate = this.props.canCreate && input.value.trim() !== ''

		return (
			<span>
				<input
					type="hidden"
					value={JSON.stringify(value)}
					name={name}
				/>

				{isSingle && (
					<Single
						input={input}
						suggestions={suggestions}
						selected={value}

						canCreate={canCreate}

						onCreate={this.handleCreate}
						onChange={this.handleChange}
						onClick={this.handleClick}
					/>
				)}

				{!isSingle && (
					<Multi
						input={input}
						suggestions={suggestions}
						selections={value || Multi.defaultProps.selections}

						canCreate={canCreate}

						onCreate={this.handleCreate}
						onChange={this.handleChange}
						onClick={this.handleClick}
					/>
				)}
			</span>
		)
	}
}


Autocomplete.propTypes = {
	name: PropTypes.string.isRequired,
	type: PropTypes.string.isRequired,
	canCreate: PropTypes.bool.isRequired,
	isSingle: PropTypes.bool.isRequired,
}


window.renderAutocompleteWidget = (id, name, value, type, canCreate, isSingle) => {
	render(
		<Autocomplete
			name={name}
			value={value}
			type={type}
			canCreate={canCreate}
			isSingle={isSingle}
		/>,
		document.getElementById(id)
	)
}
