function parseCategories(urlParams, filterName, filters) {
	let params = urlParams[filterName]
	let result
	// Set-up object with keys as integer ids, values as titles.
	let categories = Object.fromEntries(filters.filter(({id}) => id > 0).map(
		({id, title}) => [id, title]
	))

	if (params) {
		result = new Set(params.split(',').map((param) => {
			// +string evaluates to NaN if string is not numeric
			if (categories[+param]) {
				return categories[+param]
			} else {
				return param
			}
		}))
	} else {
		result = new Set()
	}

	return {
		enabled: true,
		type: 'stringset',
		parameters: result,
	}
}

function parseDateRange(urlParams, filterName, filters) {
	let lowerValue = urlParams[`${filterName}_lower`]
	let upperValue = urlParams[`${filterName}_upper`]
	return {
		enabled: false,
		type: 'date',
		parameters: {
			min: lowerValue ? new Date(lowerValue) : null,
			max: upperValue ? new Date(upperValue) : null,
		},
	}
}

function parseString(urlParams, filterName, filters) {
	return {
		enabled: false,
		type: 'string',
		parameters: urlParams[filterName],
	}
}

function parseStringSet(urlParams, filterName, filters) {
	let params = urlParams[filterName]
	let result
	if (params) {
		result = new Set(params.split(','))
	} else {
		result = new Set()
	}
	return {
		enabled: true,
		type: 'stringset',
		parameters: result,
	}
}

const queryFields = {
	date: parseDateRange,
	detention_date: parseDateRange,
	release_date: parseDateRange,

	search: parseString,
	recently_updated: parseString,
	city: parseString,
	state: parseString,
	targeted_journalists: parseString,
	targeted_institutions: parseString,
	lawsuit_name: parseString,
	venue: parseString,
	case_statuses: parseString,
	case_type: parseString,
	case_number: parseString,
	arrest_status: parseString,
	arresting_authority: parseString,
	status_of_charges: parseString,
	charges: parseString,
	unnecessary_use_of_force: parseString,
	border_point: parseString,
	stopped_previously: parseString,
	target_us_citizenship_status: parseString,
	denial_of_entry: parseString,
	target_nationality: parseString,
	did_authorities_ask_for_device_access: parseString,
	did_authorities_ask_about_work: parseString,
	politicians_or_public_figures_involved: parseString,
	equipment_seized: parseString,
	status_of_seized_equipment: parseString,
	is_search_warrant_obtained: parseString,
	actor: parseString,
	assailant: parseString,
	was_journalist_targeted: parseString,
	charged_under_espionage_act: parseString,
	subpoena_type: parseString,
	subpoena_statuses: parseString,
	held_in_contempt: parseString,
	detention_status: parseString,
	third_party_business: parseString,
	legal_order_type: parseString,
	equipment_broken: parseString,
	status_of_prior_restraint: parseString,
	legal_order_target: parseString,
	legal_order_venue: parseString,
	legal_order_status: parseString,
	legal_order_information_requested: parseString,
	third_party_in_possession_of_communications: parseString,

	tags: parseStringSet,
	categories: parseCategories,
}

export function decode(searchParams, filters) {
	let r = {}
	for (const [filterName, parseFn] of Object.entries(queryFields)) {
		r[filterName] = parseFn(searchParams, filterName, filters)
	}
	return r
}
