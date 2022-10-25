function parseDateRange(urlParams, filterName) {
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

function parseString(urlParams, filterName) {
	return {
		enabled: false,
		type: 'string',
		parameters: urlParams[filterName],
	}
}

function parseStringSet(urlParams, filterName) {
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
	arrest_status: parseString,
	arresting_authority: parseString,
	status_of_charges: parseString,
	charges: parseString,
	unnecessary_use_of_force: parseString,
	border_point: parseString,
	stopped_at_border: parseString,
	stopped_previously: parseString,
	target_us_citizenship_status: parseString,
	denial_of_entry: parseString,
	target_nationality: parseString,
	did_authorities_ask_for_device_access: parseString,
	did_authorities_ask_for_social_media_user: parseString,
	did_authorities_ask_for_social_media_pass: parseString,
	did_authorities_ask_about_work: parseString,
	were_devices_searched_or_seized: parseString,
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

	tags: parseStringSet,
	categories: parseStringSet,
}

export function decode(searchParams) {
	let r = {}
	for (const [filterName, parseFn] of Object.entries(queryFields)) {
		r[filterName] = parseFn(searchParams, filterName)
	}
	return r
}
