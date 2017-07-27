import React, { PureComponent } from 'react'
import Autocomplete from 'WagtailAutocomplete/Autocomplete'
import classNames from 'classnames'
import DatePicker from 'react-datepicker'
import Moment from 'moment'


export function AutocompleteInput({
	handleFilterChange,
	filterValues,
	label,
	filter,
	type,
	isSingle,
}) {
	return (
		<div className="filters__input-row">
			<span className="filters__input-label">{label}</span>
			<Autocomplete
				type={type}
				name={filter}
				canCreate={false}
				isSingle={isSingle}
				value={filterValues[filter]}
				onChange={handleFilterChange.bind(null, filter)}
				fetchInitialValues={true}
				apiBase="/autocomplete/"
				controlled={true}
			/>
		</div>
	)
}


export class RadioPillInput extends PureComponent {
	constructor(...args) {
		super(...args)

		this.handleClick = this.handleClick.bind(this)
	}

	handleClick(event) {
		const {
			handleFilterChange,
			filterValues,
			filter,
		} = this.props

		const { value } = event.target
		if (!value) {
			return
		}

		if (value === filterValues[filter]) {
			handleFilterChange(filter, { target: { value: '' } })
		} else {
			handleFilterChange(filter, event)
		}
	}

	render() {
		const {
			handleFilterChange,
			filterValues,
			label,
			filter,
			options,
		} = this.props

		return (
			<div className="filters__input-row">
				<span className="filters__input-label">{label}</span>

				<span className="radio-pill">
					{options.map(option => (
						<button
							key={option.value}
							value={option.value}
							type="button"
							onClick={this.handleClick}
							className={classNames(
								'radio-pill__item',
								{ 'radio-pill__item--selected': filterValues[filter] === option.value }
							)}
						>
							{option.label}
						</button>
					))}
				</span>
			</div>
		)
	}
}


RadioPillInput.defaultProps = {
	options: [
		{ label: 'Unknown', value: 'NOTHING' },
		{ label: 'Yes', value: 'JUST_TRUE' },
		{ label: 'No', value: 'JUST_FALSE' },
	],
}


export function TextInput({ handleFilterChange, filterValues, label, filter }) {
	const value = filterValues[filter] || ''
	return (
		<div className="filters__input-row">
			<span className="filters__input-label">{label}</span>
			<span>
				<input
					type="text"
					onChange={handleFilterChange.bind(null, filter)}
					value={value}
					className={classNames(
						'filter-text-input',
						{ 'filter-text-input--has-input': value.length > 0 }
					)}
				/>
			</span>
		</div>
	)
}


export function BoolInput({ handleFilterChange, filterValues, label, filter }) {
	return (
		<div className="filters__input-row">
			<span className="filters__input-label">{label}</span>
			<span>
				<input
					type="checkbox"
					onChange={handleFilterChange.bind(null, filter)}
					value={filterValues[filter] || false}
				/>
			</span>
		</div>
	)
}


export function ChoiceInput({ handleFilterChange, filterValues, label, filter, choices }) {
	return (
		<div className="filters__input-row">
			<span className="filters__input-label">{label}</span>
			<span>
				<select
					onChange={handleFilterChange.bind(null, filter)}
					value={filterValues[filter] || ''}
					className={classNames(
						'choice-input',
						{ 'choice-input--no-input': !filterValues[filter] }
					)}
				>
					<option value=""></option>
					{choices.map(choice => (
						<option
							key={choice.value}
							value={choice.value}
						>
							{choice.label}
						</option>
					))}
				</select>
			</span>
		</div>
	)
}


export class DateRangeInput extends PureComponent {
	handleChangeRaw(filter_key, evt) {
		if (!evt.target || !evt.target.value) {
			return
		}
		const value = evt.target.value
		const DATE_TYPES = [
			'MM/DD/YYYY',
			'MM-DD-YYYY',
			'MM/DD/YY',
			'MM-DD-YY',
			'YYYY-MM-DD'
		]
		const moment = Moment(value, DATE_TYPES, true)

		if (moment.isValid()) {
			this.props.handleFilterChange(filter_key, moment)
		}
	}

	render() {
		const { handleFilterChange, filterValues, label, filter } = this.props
		const filter_upper = `${filter}_upper`
		const filter_lower = `${filter}_lower`

		return (
			<div className="filters__input-row">
				<span className="filters__input-label">{label}</span>
				<span>
					<span className="filters__date-picker">
						<DatePicker
							onChange={handleFilterChange.bind(null, filter_lower)}
							onChangeRaw={this.handleChangeRaw.bind(this, filter_lower)}
							selected={filterValues[filter_lower] || ''}
							isClearable={true}
							className={classNames(
								'filter-date-picker',
								{ 'filter-date-picker--has-input': !!filterValues[filter_lower] }
							)}
						/>
					</span>
					{' '}
					<span className="filters__space">and</span>
					{' '}
					<span className="filters__date-picker">
						<DatePicker
							onChange={handleFilterChange.bind(null, filter_upper)}
							selected={filterValues[filter_upper] || ''}
							isClearable={true}
							className={classNames(
								'filter-date-picker',
								{ 'filter-date-picker--has-input': !!filterValues[filter_upper] }
							)}
						/>
					</span>
				</span>
			</div>
		)
	}
}
