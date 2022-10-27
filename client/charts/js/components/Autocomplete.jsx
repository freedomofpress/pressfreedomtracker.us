import React, {useReducer, useEffect} from 'react'
import classNames from "classnames"

import PropTypes from 'prop-types'


const initialState = {
	// The active selection's index
    activeSuggestion: 0,
    // The suggestions that match the user's input
    filteredSuggestions: [],
    // Whether or not the suggestion list is shown
    showSuggestions: false,
    // What the user has entered
    userInput: ""
}

const propTypes = {
	suggestions: PropTypes.array.isRequired,
	suggestionsLabelField: PropTypes.string.isRequired,
	suggestionsSidenoteField: PropTypes.string.isRequired,
	name: PropTypes.string.isRequired,
	placeholder: PropTypes.string.isRequired,
	handleSelect: PropTypes.func.isRequired,
	itemNamePlural: PropTypes.string.isRequired,
}

const filterSuggestions = query => ({
	type: 'FILTER_SUGGESTIONS',
	payload: query,
})


const selectSuggestion = query => ({
	type: 'SELECT_SUGGESTION',
	payload: query,
})


const AutoComplete = ({
	suggestions,
	suggestionsLabelField,
	suggestionsSidenoteField,
	name,
	placeholder,
	handleSelect,
	itemNameSingular,
	itemNamePlural,
}) => {
	const reducer = (state, {type, payload}) => {
		switch (type) {
			case 'SELECT_SUGGESTION':
				return initialState
			case 'FILTER_SUGGESTIONS':
				const filteredSuggestions = suggestions.filter(
					suggestion =>
					suggestion[suggestionsLabelField].toLowerCase().indexOf(payload.toLowerCase()) > -1
				)
				return {
					activeSuggestion: 0,
					filteredSuggestions,
					userInput: payload,
					showSuggestions: true,
				}

			default:
				throw new Error(`Unknown action type: ${type}`)
		}
	}

	const [state, dispatch] = useReducer(reducer, initialState)

	const id = `id_${name}`
	const choicesId = `${name}_choices`
	const onChange = (event) => dispatch(filterSuggestions(event.target.value))
	const onClick = (event) => {
		let val = event.currentTarget.dataset.item
		handleSelect(val)
		dispatch(selectSuggestion(val))
	}

	let suggestionListComponent
	if (state.showSuggestions && state.userInput) {
		if (state.filteredSuggestions.length) {
			suggestionListComponent = (
				<ul className="filters__suggestions">
					{state.filteredSuggestions.map((suggestion, index) => (
						<li
							className="filters__suggestions-item filters__suggestions-item--selectable"
							onClick={onClick}
							data-item={suggestion[suggestionsLabelField]}
							key={index}
						>
							<span>
								{suggestion[suggestionsLabelField]}
								<span
									className="filters__suggestion-tooltip"
								>
									&ndash;
									<span
										className="filters__suggestion-tooltip-text"
									>
										Add {itemNameSingular}
									</span>
								</span>
							</span>
							<span>{suggestion[suggestionsSidenoteField]}</span>
						</li>
					))}
				</ul>
			)
		} else {
			suggestionListComponent = (
				<ul className="filters__suggestions">
					<li className="filters__suggestions-item">
						No {itemNamePlural} found
					</li>
				</ul>
			)
		}
	}

	return (
		<>
			<input
				type="text"
				name={name}
				className="text-field--single"
				autoComplete="off"
				onChange={onChange}
				id={id}
				placeholder={placeholder}
				value={state.userInput}
			/>
			{suggestionListComponent}
		</>
	)
}


AutoComplete.propTypes = propTypes

export default AutoComplete
