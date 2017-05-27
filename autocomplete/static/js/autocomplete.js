import React, { PureComponent } from 'react'
import { render } from 'react-dom'
import PropTypes from 'prop-types'
import axios from 'axios'
import classNames from 'classnames'


axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


class Suggestions extends PureComponent {
	constructor(...args) {
		super(...args)

		this.handleKeyPress = this.handleKeyPress.bind(this)

		this.state = {
			index: 0,
		}
	}

	componentDidMount() {
	}

	componentWillReceiveProps(nextProps) {
		if (this.shouldResetIndex(nextProps)) {
			this.setState({
				index: 0,
			})
		}
	}

	/**
	 * If the suggestion at the curent index has changed, the index
	 * needs to be reset.
	 */
	shouldResetIndex(nextProps) {
		const { suggestions } = this.props
		if (suggestions.length === 0) {
			return true
		}

		const { index } = this.state
		if (index >= nextProps.suggestions.length) {
			return true
		}

		const currentId = suggestions[index].id
		return nextProps.suggestions[index].id !== currentId
	}

	handleKeyPress(event) {
	}

	render() {
		const {
			suggestions,
			canCreate,
			onClick,
			onCreate,
			onChange,
			input,
		} = this.props

		return (
			<span>
				<input
					type="text"
					className={classNames('autocomplete__search', { 'autocomplete__search--has-input': suggestions.length > 0 })}
					onChange={onChange}
					{...input}
				/>

				<ul
					className={classNames(
						'suggestions',
						{ 'suggestions--populated': suggestions.length > 0 }
					)}
				>
					{suggestions.map(suggestion =>
						<li
							key={suggestion.id}
							onClick={onClick.bind(null, suggestion)}
							className="suggestions__item"
						>
							<span>{suggestion.label}</span>
							<svg viewBox="0 0 1792 1792" xmlns="http://www.w3.org/2000/svg"><path d="M1600 960q0 54-37 91l-651 651q-39 37-91 37-51 0-90-37l-75-75q-38-38-38-91t38-91l293-293h-704q-52 0-84.5-37.5t-32.5-90.5v-128q0-53 32.5-90.5t84.5-37.5h704l-293-294q-38-36-38-90t38-90l75-75q38-38 90-38 53 0 91 38l651 651q37 35 37 90z"/></svg>
						</li>
					)}

					{canCreate && (
						<li
							key="create"
							onClick={onCreate}
							className="suggestions__item--create"
						>
							Create new “{input.value}”
						</li>
					)}
				</ul>
			</span>
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
			<Suggestions
				suggestions={suggestions}
				onClick={onClick}
				onCreate={onCreate}
				onChange={onChange}
				canCreate={canCreate}
				input={input}
			/>
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
			<span className="autocomplete-layout">
				<span className="autocomplete-layout__item">
					<h3>Search</h3>
					<Suggestions
						suggestions={suggestions}
						onClick={this.handleClick}
						onChange={onChange}
						onCreate={onCreate}
						canCreate={canCreate}
						input={input}
						inputElm={this.inputElm}
					/>
				</span>

				<span className="autocomplete-layout__item">
					<h3>Selected</h3>
					{selections.length === 0 && (
						<span>Nothing selected.</span>
					)}
					{selections.map(selection =>
						<div
							key={selection.id}
							className="selection"
						>
							<span className="selection__label">{selection.label}</span>

							<button
								type="button"
								className="selection__button"
								onClick={this.handleRemove.bind(this, selection)}
							>
								<svg className="selection__icon" viewBox="0 0 1792 1792" xmlns="http://www.w3.org/2000/svg"><path d="M1490 1322q0 40-28 68l-136 136q-28 28-68 28t-68-28l-294-294-294 294q-28 28-68 28t-68-28l-136-136q-28-28-28-68t28-68l294-294-294-294q-28-28-28-68t28-68l136-136q28-28 68-28t68 28l294 294 294-294q28-28 68-28t68 28l136 136q28 28 28 68t-28 68l-294 294 294 294q28 28 28 68z"/></svg>
								<span className="sr-only">Remove</span>
							</button>
						</div>
					)}
				</span>
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
			<span className="autocomplete">
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
