import React from 'react'
import {
	AutocompleteInput,
	BoolInput,
	ChoiceInput,
	DateRangeInput,
	TextInput,
	RadioPillInput,
} from '~/filtering/Inputs'


function FilterSet({ children }) {
	return (
		<div className="filters__set">
			{children}
		</div>
	)
}


const FilterSets = {}


FilterSets['General'] = function({ handleFilterChange, filterValues }) {
	return (
		<FilterSet>
			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Search Terms"
				filter="search"
			/>

			<DateRangeInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Took place between"
				filter="date"
			/>

			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Affiliation"
				filter="affiliation"
			/>

			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="City"
				filter="city"
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="State"
				filter="state"
				type="incident.State"
				isSingle={true}
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Targeted any of these journalists"
				filter="targets"
				type="incident.Target"
				isSingle={false}
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Has any of these tags"
				filter="tags"
				type="common.CommonTag"
				isSingle={false}
			/>

			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Lawsuit Name"
				filter="lawsuit_name"
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Venue"
				filter="venue"
				type="incident.Venue"
				isSingle={true}
			/>
		</FilterSet>
	)
}


FilterSets['General'].fields = [
	'search',
	'date_lower',
	'date_upper',
	'affiliation',
	'city',
	'state',
	'targets',
	'tags',
	'lawsuit_name',
	'venue',
]


const arrestSets = function({ handleFilterChange, filterValues, choices }) {
	return (
		<FilterSet>
			<BoolInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Unnecessary use of force?"
				filter="unnecessary_use_of_force"
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Arrest status"
				filter="arrest_status"
				choices={choices.ARREST_STATUS}
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Status of charges"
				filter="status_of_charges"
				choices={choices.STATUS_OF_CHARGES}
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Charges"
				filter="charges"
				type="incident.Charge"
				isSingle={false}
			/>

			<DateRangeInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Detention date between"
				filter="detention_date"
			/>

			<DateRangeInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Release date between"
				filter="release_date"
			/>
		</FilterSet>
	)
}

FilterSets['Arrest / Detention'] = FilterSets['Arrest/Criminal Charge'] = FilterSets['Arrest / Criminal Charge'] = arrestSets

arrestSets.fields = [
	'unnecessary_use_of_force',
	'arrest_status',
	'status_of_charges',
	'charges',
	'detention_status',
	'detention_date_lower',
	'detention_date_upper',
	'release_date_lower',
	'release_date_upper',
]


FilterSets['Border Stop'] = function({ handleFilterChange, filterValues, choices }) {
	return (
		<FilterSet>
			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Border Point"
				filter="border_point"
			/>

			<BoolInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Stopped at border?"
				filter="stopped_at_border"
			/>

			<BoolInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Stopped previously?"
				filter="stopped_previously"
			/>

			<BoolInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Denied entry?"
				filter="denial_of_entry"
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="US Citizenship Status"
				filter="target_us_citizenship_status"
				choices={choices.CITIZENSHIP_STATUS_CHOICES}
			/>

			<RadioPillInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Did authorities ask for device access?"
				filter="did_authorities_ask_for_device_access"
			/>

			<RadioPillInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Did authorities ask for social media username?"
				filter="did_authorities_ask_for_social_media_user"
			/>

			<RadioPillInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Did authorities ask for social media password?"
				filter="did_authorities_ask_for_social_media_pass"
			/>

			<RadioPillInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Did authorities ask about work?"
				filter="did_authorities_ask_about_work"
			/>

			<RadioPillInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Were devices searched or seized?"
				filter="were_devices_searched_or_seized"
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Nationality"
				filter="target_nationality"
				type="incident.Nationality"
				isSingle={false}
			/>
		</FilterSet>
	)
}

FilterSets['Border Stop'].fields = [
	'border_point',
	'stopped_at_border',
	'stopped_previously',
	'target_us_citizenship_status',
	'denial_of_entry',
	'target_nationality',
	'did_authorities_ask_for_device_access',
	'did_authorities_ask_for_social_media_user',
	'did_authorities_ask_for_social_media_pass',
	'did_authorities_ask_about_work',
	'were_devices_searched_or_seized',
]


FilterSets['Denial of Access'] = function({ handleFilterChange, filterValues }) {
	return (
		<FilterSet>
			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Politicians or public figures involved"
				filter="politicians_or_public_figures_involved"
				type="incident.PoliticianOrPublic"
				isSingle={false}
			/>
		</FilterSet>
	)
}

FilterSets['Denial of Access'].fields = [
	'politicians_or_public_figures_involved'
]


FilterSets['Equipment Search, Seizure, or Damage'] = function({ handleFilterChange, filterValues, choices }) {
	return (
		<FilterSet>
			<BoolInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Search warrant obtained?"
				filter="is_search_warrant_obtained"
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Status of seized equipment"
				filter="status_of_seized_equipment"
				choices={choices.STATUS_OF_SEIZED_EQUIPMENT}
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Actor"
				filter="actor"
				choices={choices.ACTORS}
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Equipment seized includes any of"
				filter="equipment_seized"
				type="incident.Equipment"
				isSingle={false}
			/>

			<AutocompleteInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Equipment broken includes any of"
				filter="equipment_broken"
				type="incident.Equipment"
				isSingle={false}
			/>
		</FilterSet>
	)
}

FilterSets['Equipment Search, Seizure, or Damage'].fields = [
	'equipment_seized',
	'equipment_broken',
	'status_of_seized_equipment',
	'is_search_warrant_obtained',
	'actor',
]

FilterSets['Leak Case'] = function({ handleFilterChange, filterValues }) {
	return (
		<FilterSet>
			<BoolInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Charged under espionage act?"
				filter="charged_under_espionage_act"
			/>
		</FilterSet>
	)
}

FilterSets['Leak Case'].fields = [
	"charged_under_espionage_act"
]


FilterSets['Physical Attack'] = function({ handleFilterChange, filterValues, choices }) {
	return (
		<FilterSet>
			<RadioPillInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Was journalist targeted?"
				filter="was_journalist_targeted"
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Assailant"
				filter="assailant"
				choices={choices.ACTORS}
			/>
		</FilterSet>
	)
}

FilterSets['Physical Attack'].fields = [
	'assailant',
	'was_journalist_targeted',
]


FilterSets['Subpoena / Legal Order'] = function({ handleFilterChange, filterValues, choices }) {
	return (
		<FilterSet>
			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Subpoena subject"
				filter="subpoena_subject"
				choices={choices.SUBPOENA_SUBJECT}
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Subpoena type"
				filter="subpoena_type"
				choices={choices.SUBPOENA_TYPE}
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Subpoena status"
				filter="subpoena_status"
				choices={choices.SUBPOENA_STATUS}
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Detention status"
				filter="detention_status"
				choices={choices.DETENTION_STATUS}
			/>

			<TextInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Third party in possession of communications"
				filter="third_party_in_possession_of_communications"
			/>

			<RadioPillInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Held in contempt?"
				filter="held_in_contempt"
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Third party business"
				filter="third_party_business"
				choices={choices.THIRD_PARTY_BUSINESS}
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Legal order type"
				filter="legal_order_type"
				choices={choices.LEGAL_ORDER_TYPES}
			/>

			<ChoiceInput
				handleFilterChange={handleFilterChange}
				filterValues={filterValues}
				label="Status of prior restraint"
				filter="status_of_prior_restraint"
				choices={choices.PRIOR_RESTRAINT_STATUS}
			/>
		</FilterSet>
	)
}

FilterSets['Subpoena / Legal Order'].fields = [
		'third_party_in_possession_of_communications',
		'third_party_business',
		'legal_order_type',
		'status_of_prior_restraint',
		'subpoena_subject',
		'subpoena_type',
		'subpoena_status',
		'held_in_contempt',
		'detention_status',
	]


export default FilterSets
