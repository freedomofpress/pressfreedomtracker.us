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


const incrementActiveSuggestion = {
	type: 'INCREMENT_ACTIVE_SUGGESTION',
	payload: null,
}


const decrementActiveSuggestion = {
	type: 'DECREMENT_ACTIVE_SUGGESTION',
	payload: null,
}


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
			case 'DECREMENT_ACTIVE_SUGGESTION':
				return {...state, activeSuggestion: Math.max(0, state.activeSuggestion - 1)}
			case 'INCREMENT_ACTIVE_SUGGESTION':
				return {...state, activeSuggestion: Math.min(state.filteredSuggestions.length - 1, state.activeSuggestion + 1)}
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

	const onKeyDown = (event) => {
		if (event.keyCode === 13) { // Enter key
			let val = state.filteredSuggestions[state.activeSuggestion][suggestionsLabelField]
			handleSelect(val)
			dispatch(selectSuggestion(val))

		} else if (event.keyCode === 38) { // up arrow
			dispatch(decrementActiveSuggestion)
		} else if (event.keyCode === 40) { // down arrow
			dispatch(incrementActiveSuggestion)
		}
	}

	let suggestionListComponent
	if (state.showSuggestions && state.userInput) {
		if (state.filteredSuggestions.length) {
			suggestionListComponent = (
				<ul className="filters__suggestions">
					{state.filteredSuggestions.map((suggestion, index) => (
						<li
							className="filters__suggestions-item filters__suggestions-item--selectable"
							className={classNames("filters__suggestions-item", "filters__suggestions-item--selectable", {"filters__suggestions-item--active": index === state.activeSuggestion})}
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
				onKeyDown={onKeyDown}
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
