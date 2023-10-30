import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import GeneralFilter from '../GeneralFilter'

test('renders CheckBoxesYear with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<GeneralFilter
			filterDef={{
				"id": -1,
				"title": "General",
				"filters": [
					{
						"title": "Search terms",
						"type": "text",
						"name": "search"
					},
					{
						"title": "Took place",
						"type": "date",
						"name": "date"
					},
					{
						"title": "Updated in the last",
						"type": "int",
						"name": "recently_updated",
						"units": "days"
					},
					{
						"title": "City",
						"type": "text",
						"name": "city"
					},
					{
						"title": "State",
						"type": "autocomplete",
						"name": "state",
						"autocomplete_type": "incident.State",
						"choices": [
							"Alaska",
							"Alabama",
							"Arkansas",
							"American Samoa",
							"Arizona",
							"California",
							"Colorado",
							"Connecticut",
							"District of Columbia",
							"Delaware",
							"Florida"
						],
						"many": false
					},
					{
						"title": "Targeted any of these journalists",
						"type": "autocomplete",
						"name": "targeted_journalists",
						"autocomplete_type": "incident.Journalist",
						"choices": [
							"Abigail Peterson",
							"Adam Buchanan",
							"Adam Lopez MD",
							"Alicia Savage",
							"Amanda Rosales",
							"Angela Davis",
							"Angela Johnson",
							"Anthony Black",
							"Anthony Ellison",
							"Anthony Poole",
							"April Olson",
							"Ariel Hill",
							"Austin Henry"
						],
						"many": true
					},
					{
						"title": "Targeted Institutions",
						"type": "autocomplete",
						"name": "targeted_institutions",
						"autocomplete_type": "incident.Institution",
						"choices": [
							"The Aaronmouth Post 141",
							"The Alexanderbury Sun 191",
							"The Alexisberg Post 155",
							"The Amberport Tribune 100",
							"The Andrewview Tribune 39",
							"The Annaberg Tribune 145",
							"The Anneside Post 41",
							"The Ashleymouth Tribune 184",
							"The Austinborough Sun 164",
							"The Banksberg Herald 142",
							"The Batesland Post 126",
							"The Beckyview Daily News 128",
							"The Bellburgh Post 135",
							"The Benderton Sun 102",
							"The Bethfort Daily News 7",
							"The Blevinsland Tribune 200",
							"The Bobbymouth Tribune 170",
							"The Bradleyshire Herald 198",
							"The Brittanyshire Sun 74",
							"The Brownview Daily News 148",
							"The Bryantmouth Daily News 11",
							"The Burtonview Daily News 207",
							"The Byrdbury Herald 26",
							"The Candiceburgh Post 193"
						],
						"many": true
					},
					{
						"title": "Has any of these tags",
						"type": "autocomplete",
						"name": "tags",
						"autocomplete_type": "common.CommonTag",
						"choices": [
							"ammonites",
							"ants",
							"aphids",
							"baboon",
							"bamboo",
							"bees",
							"centipedes"
						],
						"many": true
					},
					{
						"title": "Case number",
						"type": "text",
						"name": "case_number"
					},
					{
						"title": "Type of case",
						"type": "choice",
						"name": "case_type",
						"choices": [
							[
								"CIVIL",
								"Civil"
							],
							[
								"CLASS_ACTION",
								"Class Action"
							]
						]
					},
					{
						"title": "Legal case statuses",
						"type": "choice",
						"name": "case_statuses",
						"choices": [
							[
								"ONGOING",
								"ongoing"
							],
							[
								"SETTLED",
								"settled"
							],
							[
								"DISMISSED",
								"dismissed"
							],
							[
								"UNKNOWN",
								"unknown"
							],
							[
								"APPEALED",
								"appealed"
							]
						]
					}
				]
			}}
			filterParameters={{
				"filterTimeMonths": {
					"type": "timeMonths",
					"parameters": {
						"min": "2022-03-20T00:00:00.000Z",
						"max": "2023-02-18T00:00:00.000Z"
					},
					"enabled": true
				},
				"filterTimeYears": {
					"type": "timeYears",
					"parameters": [
						2022,
						2023
					],
					"enabled": false
				},
				"filterState": {
					"type": "state",
					"parameters": "All",
					"enabled": true
				},
				"date": {
					"enabled": false,
					"type": "date",
					"parameters": {
						"min": null,
						"max": null
					}
				},
				"detention_date": {
					"enabled": false,
					"type": "date",
					"parameters": {
						"min": null,
						"max": null
					}
				},
				"release_date": {
					"enabled": false,
					"type": "date",
					"parameters": {
						"min": null,
						"max": null
					}
				},
				"search": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"recently_updated": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"city": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"state": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"targeted_journalists": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"targeted_institutions": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"lawsuit_name": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"venue": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"case_statuses": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"case_type": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"case_number": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"arrest_status": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"arresting_authority": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"status_of_charges": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"charges": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"unnecessary_use_of_force": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"border_point": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"stopped_previously": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"target_us_citizenship_status": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"denial_of_entry": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"target_nationality": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"did_authorities_ask_for_device_access": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"did_authorities_ask_about_work": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"politicians_or_public_figures_involved": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"equipment_seized": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"status_of_seized_equipment": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"is_search_warrant_obtained": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"actor": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"assailant": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"was_journalist_targeted": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"charged_under_espionage_act": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"subpoena_type": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"subpoena_statuses": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"held_in_contempt": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"detention_status": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"third_party_business": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"legal_order_type": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"equipment_broken": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"status_of_prior_restraint": {
					"enabled": false,
					"type": "string",
					"parameters": null
				},
				"tags": {
					"enabled": true,
					"type": "stringset",
					"parameters": {}
				},
				"categories": {
					"enabled": true,
					"type": "stringset",
					"parameters": {}
				}
			}}
			width={200}
			dataset={[]}
		/>
	)).toMatchSnapshot();
});
