import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import axios from 'axios'

import Single from './Single'
import Multi from './Multi'


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

		if (props.fetchInitialValues) {
			this.fetchInitialValues(props.value)
		}
	}

	componentDidMount() {
		this.checkNewSuggestions('', false)
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

		if (typeof this.props.onChange === 'function') {
			this.props.onChange({ target: { value } })
		}
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

	checkNewSuggestions(value, checkDifferent = true) {
		if (checkDifferent && value === this.state.value) {
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

				if (!Array.isArray(res.data.pages)) {
					return
				}

				this.setState({
					suggestions: res.data.pages
				})
			})
	}

	fetchInitialValues(value) {
		if (!value || value.length === 0) {
			return
		}

		const params = {
			ids: value.map(({ id }) => id).join(','),
			type: this.props.type,
		}
		axios.get('/autocomplete/objects/', { params })
			.then(res => {
				if (res.status !== 200) {
					return
				}

				if (!Array.isArray(res.data.pages)) {
					return
				}

				const value = this.state.value.map(value => {
					const page = res.data.pages.find(page => page.id === value.id)
					if (!page) {
						return value
					}

					return page
				})

				this.setState({ value })
			})
	}

	handleClick(value) {
		this.setState({ value })

		if (typeof this.props.onChange === 'function') {
			this.props.onChange({ target: { value } })
		}
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

				const value = this.props.isSingle ? res.data : (this.state.value || []).concat(res.data)

				this.setState({
					isLoading: false,
					value,
				})

				if (typeof this.props.onChange === 'function') {
					this.props.onChange({ target: { value } })
				}
			})
		this.setState({ isLoading: true })
	}

	render() {
		const { name, isSingle, onChange } = this.props
		const { value, input, suggestions } = this.state

		const canCreate = this.props.canCreate && input.value.trim() !== ''
		const useHiddenInput = typeof onChange !== 'function'

		return (
			<span className="autocomplete">
				{useHiddenInput && (
					<input
						type="hidden"
						value={JSON.stringify(value)}
						name={name}
					/>
				)}

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


Autocomplete.defaultProps = {
	fetchInitialValues: false,
}


Autocomplete.propTypes = {
	name: PropTypes.string.isRequired,
	type: PropTypes.string.isRequired,
	canCreate: PropTypes.bool.isRequired,
	isSingle: PropTypes.bool.isRequired,
	onChange: PropTypes.func,
	fetchInitialValues: PropTypes.bool,
}


export default Autocomplete
