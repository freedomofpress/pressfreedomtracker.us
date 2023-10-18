import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import FiltersIntegration from '../FiltersIntegration'

test('renders FiltersIntegration with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<FiltersIntegration
			width={500}
			dataset={[
				{
					"date": "2023-02-12T00:00:00.000Z",
					"city": "Thomasland",
					"state": "ID",
					"latitude": null,
					"longitude": null,
					"categories": "Arrest / Criminal Charge",
					"tags": "lemur"
				},
				{
					"date": "2022-10-23T00:00:00.000Z",
					"city": "New Brooke",
					"state": "NC",
					"latitude": null,
					"longitude": null,
					"categories": "Arrest / Criminal Charge",
					"tags": "baboon"
				},
				{
					"date": "2022-05-12T00:00:00.000Z",
					"city": "East Mary",
					"state": "CT",
					"latitude": null,
					"longitude": null,
					"categories": "Equipment Search or Seizure",
					"tags": "civet"
				},
				{
					"date": "2022-07-24T00:00:00.000Z",
					"city": "Josephmouth",
					"state": "AL",
					"latitude": null,
					"longitude": null,
					"categories": "Equipment Search or Seizure",
					"tags": "hyena"
				},
				{
					"date": "2022-04-12T00:00:00.000Z",
					"city": "North Nancystad",
					"state": "WV",
					"latitude": null,
					"longitude": null,
					"categories": "Border Stop",
					"tags": "chrysanthemum"
				},
				{
					"date": "2022-09-02T00:00:00.000Z",
					"city": "East Kaitlyn",
					"state": "OH",
					"latitude": null,
					"longitude": null,
					"categories": "Border Stop",
					"tags": "plum"
				},
				{
					"date": "2023-01-16T00:00:00.000Z",
					"city": "New Jamesberg",
					"state": "TX",
					"latitude": null,
					"longitude": null,
					"categories": "Assault",
					"tags": "platypus"
				}
			]}
			initialFilterParams={{
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
				"were_devices_searched_or_seized": {
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
			filters={[
				{
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
								"Florida",
								"Georgia",
								"Guam",
								"Hawaii",
								"Iowa",
								"Idaho",
								"Illinois",
								"Indiana",
								"Kansas",
								"Kentucky",
								"Louisiana",
								"Massachusetts",
								"Maryland",
								"Maine",
								"Michigan",
								"Minnesota",
								"Missouri",
								"Northern Mariana Islands",
								"Mississippi",
								"Montana",
								"North Carolina",
								"North Dakota",
								"Nebraska",
								"New Hampshire",
								"New Jersey",
								"New Mexico",
								"Nevada",
								"New York",
								"Ohio",
								"Oklahoma",
								"Oregon",
								"Pennsylvania",
								"Puerto Rico",
								"Rhode Island",
								"South Carolina",
								"South Dakota",
								"Tennessee",
								"Texas",
								"Utah",
								"Virginia",
								"Virgin Islands",
								"Vermont",
								"Washington",
								"Wisconsin",
								"West Virginia",
								"Wyoming"
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
								"Austin Henry",
								"Brandi White",
								"Candace Glover",
								"Carl Hall",
								"Cassie Wall"
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
								"The Bellburgh Post 135"
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
								"centipedes",
								"chrysanthemum",
								"civet",
								"clams",
								"copepods",
								"crabs",
								"crickets"
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
				},
				{
					"id": 4,
					"title": "Arrest / Criminal Charge",
					"url": "/arrest-criminal-charge/",
					"symbol": "arrest",
					"filters": [
						{
							"title": "Arrest status",
							"type": "choice",
							"name": "arrest_status",
							"choices": [
								[
									"UNKNOWN",
									"unknown"
								],
								[
									"DETAINED_NO_PROCESSING",
									"detained and released without being processed"
								],
								[
									"DETAINED_CUSTODY",
									"detained and still in custody"
								],
								[
									"ARRESTED_CUSTODY",
									"arrested and still in custody"
								],
								[
									"ARRESTED_RELEASED",
									"arrested and released"
								],
								[
									"CHARGED_WITHOUT_ARREST",
									"charged without arrest"
								]
							]
						},
						{
							"title": "Arresting authority",
							"type": "autocomplete",
							"name": "arresting_authority",
							"autocomplete_type": "incident.LawEnforcementOrganization",
							"choices": [
								"Aaronstad Security Forces",
								"Adamsside Security Forces",
								"Ambertown Military Police",
								"Amyside Police Squad",
								"Armstrongton Public Safety Officers",
								"Boonefurt Police Squad",
								"Bradleyland Police Department",
								"Buchananfort Police Squad",
								"Charlesberg Police Squad",
								"Comptonburgh Security Forces"
							],
							"many": false
						},
						{
							"title": "Status of charges",
							"type": "choice",
							"name": "status_of_charges",
							"choices": [
								[
									"UNKNOWN",
									"unknown"
								],
								[
									"NOT_CHARGED",
									"not charged"
								],
								[
									"CHARGES_PENDING",
									"charges pending"
								],
								[
									"CHARGES_DROPPED",
									"charges dropped"
								],
								[
									"CONVICTED",
									"convicted"
								],
								[
									"ACQUITTED",
									"acquitted"
								],
								[
									"PENDING_APPEAL",
									"pending appeal"
								]
							]
						},
						{
							"title": "Detention date",
							"type": "date",
							"name": "detention_date"
						},
						{
							"title": "Release date",
							"type": "date",
							"name": "release_date"
						},
						{
							"title": "Unnecessary use of force?",
							"type": "bool",
							"name": "unnecessary_use_of_force"
						},
						{
							"title": "Charges",
							"type": "autocomplete",
							"name": "charges",
							"choices": [
								"antisocial bootlegging",
								"antisocial calumny",
								"antisocial cybercrime",
								"antisocial espionage",
								"antisocial hacking",
								"antisocial hooliganism",
								"antisocial misdeeds",
								"antisocial piracy",
								"antisocial plagiarism"
							],
							"autocomplete_type": "incident.Charge"
						}
					]
				},
				{
					"id": 5,
					"title": "Border Stop",
					"url": "/border-stop/",
					"symbol": "border_stop",
					"filters": [
						{
							"title": "Border point",
							"type": "text",
							"name": "border_point"
						},
						{
							"title": "Stopped previously?",
							"type": "bool",
							"name": "stopped_previously"
						},
						{
							"title": "US Citizenship Status",
							"type": "choice",
							"name": "target_us_citizenship_status",
							"choices": [
								[
									"US_CITIZEN",
									"U.S. citizen"
								],
								[
									"PERMANENT_RESIDENT",
									"U.S. permanent resident (green card)"
								],
								[
									"NON_RESIDENT",
									"U.S. non-resident"
								]
							]
						},
						{
							"title": "Denied entry?",
							"type": "bool",
							"name": "denial_of_entry"
						},
						{
							"title": "Target Nationality",
							"type": "autocomplete",
							"name": "target_nationality",
							"autocomplete_type": "incident.Nationality",
							"choices": [
								"Afghanistan",
								"Andorra",
								"Anguilla",
								"Antarctica (the territory South of 60 deg S)",
								"Bahamas",
								"Belarus",
								"Belize",
								"Benin",
								"Bosnia and Herzegovina",
								"Brunei Darussalam",
								"Burkina Faso",
								"Cameroon"
							],
							"many": true
						},
						{
							"title": "Did authorities ask for device access?",
							"type": "radio",
							"name": "did_authorities_ask_for_device_access"
						},
						{
							"title": "Did authorities ask intrusive questions about journalist's work?",
							"type": "radio",
							"name": "did_authorities_ask_about_work"
						},
						{
							"title": "Were devices searched or seized?",
							"type": "radio",
							"name": "were_devices_searched_or_seized"
						}
					]
				},
				{
					"id": 6,
					"title": "Denial of Access",
					"url": "/denial-access/",
					"symbol": "denial_of_access",
					"filters": [
						{
							"title": "Government agency or public official involved",
							"type": "autocomplete",
							"name": "politicians_or_public_figures_involved",
							"autocomplete_type": "incident.PoliticianOrPublic",
							"choices": [
								"Aaron Singleton",
								"Alexandra Pitts",
								"Alexis Patterson",
								"Alicia Merritt",
								"Amber Greene",
								"Amy Russell PhD",
								"Amy Smith",
								"Andre Cole",
								"Andre Gentry",
								"Andre Patterson",
								"Andrew Bass"
							],
							"many": true
						}
					]
				},
				{
					"id": 7,
					"title": "Equipment Search or Seizure",
					"url": "/equipment-search-seizure-or-damage/",
					"symbol": "equipment_search",
					"filters": [
						{
							"title": "Equipment Seized",
							"type": "autocomplete",
							"name": "equipment_seized",
							"autocomplete_type": "incident.Equipment",
							"choices": [
								"graph paper",
								"compass",
								"planimeter",
								"photometer",
								"protractor",
								"calculator",
								"timer",
								"abacus",
								"ruler",
								"hygrometer",
								"diffuser",
								"multimeter",
								"microscope"
							],
							"many": true
						},
						{
							"title": "Status of seized equipment",
							"type": "choice",
							"name": "status_of_seized_equipment",
							"choices": [
								[
									"UNKNOWN",
									"unknown"
								],
								[
									"CUSTODY",
									"in custody"
								],
								[
									"RETURNED_FULL",
									"returned in full"
								],
								[
									"RETURNED_PART",
									"returned in part"
								]
							]
						},
						{
							"title": "Search warrant obtained?",
							"type": "bool",
							"name": "is_search_warrant_obtained"
						},
						{
							"title": "Actor",
							"type": "choice",
							"name": "actor",
							"choices": [
								[
									"UNKNOWN",
									"unknown"
								],
								[
									"LAW_ENFORCEMENT",
									"law enforcement"
								],
								[
									"PRIVATE_SECURITY",
									"private security"
								],
								[
									"POLITICIAN",
									"politician"
								],
								[
									"PUBLIC_FIGURE",
									"public figure"
								],
								[
									"PRIVATE_INDIVIDUAL",
									"private individual"
								]
							]
						}
					]
				},
				{
					"id": 8,
					"title": "Assault",
					"url": "/assault/",
					"symbol": "assault",
					"filters": [
						{
							"title": "Assailant",
							"type": "choice",
							"name": "assailant",
							"choices": [
								[
									"UNKNOWN",
									"unknown"
								],
								[
									"LAW_ENFORCEMENT",
									"law enforcement"
								],
								[
									"PRIVATE_SECURITY",
									"private security"
								],
								[
									"POLITICIAN",
									"politician"
								],
								[
									"PUBLIC_FIGURE",
									"public figure"
								],
								[
									"PRIVATE_INDIVIDUAL",
									"private individual"
								]
							]
						},
						{
							"title": "Was journalist targeted?",
							"type": "radio",
							"name": "was_journalist_targeted"
						}
					]
				},
				{
					"id": 9,
					"title": "Leak Case",
					"url": "/leak-case/",
					"symbol": "leak_case",
					"filters": [
						{
							"title": "Charged under espionage act?",
							"type": "bool",
							"name": "charged_under_espionage_act"
						}
					]
				},
				{
					"id": 10,
					"title": "Subpoena / Legal Order",
					"url": "/subpoena/",
					"symbol": "subpoena",
					"filters": [
						{
							"title": "Subpoena type",
							"type": "choice",
							"name": "subpoena_type",
							"choices": [
								[
									"TESTIMONY_ABOUT_SOURCE",
									"testimony about confidential source"
								],
								[
									"OTHER_TESTIMONY",
									"other testimony"
								],
								[
									"JOURNALIST_COMMUNICATIONS",
									"journalist communications or work product"
								]
							]
						},
						{
							"title": "Subpoena status",
							"type": "choice",
							"name": "subpoena_statuses",
							"choices": [
								[
									"UNKNOWN",
									"unknown"
								],
								[
									"PENDING",
									"pending"
								],
								[
									"DROPPED",
									"dropped"
								],
								[
									"QUASHED",
									"quashed"
								],
								[
									"UPHELD",
									"upheld"
								],
								[
									"CARRIED_OUT",
									"carried out"
								],
								[
									"IGNORED",
									"ignored"
								],
								[
									"OBJECTED_TO",
									"objected to"
								]
							]
						},
						{
							"title": "If subject refused to cooperate, were they held in contempt?",
							"type": "radio",
							"name": "held_in_contempt"
						},
						{
							"title": "Detention status",
							"type": "choice",
							"name": "detention_status",
							"choices": [
								[
									"HELD_IN_CONTEMPT_NO_JAIL",
									"held in contempt but not jailed"
								],
								[
									"IN_JAIL",
									"in jail"
								],
								[
									"RELEASED",
									"released from jail"
								]
							]
						},
						{
							"title": "Third party business",
							"type": "choice",
							"name": "third_party_business",
							"choices": [
								[
									"TELECOM",
									"telecom company"
								],
								[
									"TECH_COMPANY",
									"tech company"
								],
								[
									"ISP",
									"internet service provider"
								],
								[
									"FINANCIAL",
									"bank/financial institution"
								],
								[
									"TRAVEL",
									"travel company"
								],
								[
									"OTHER",
									"other"
								]
							]
						},
						{
							"title": "Legal order type",
							"type": "choice",
							"name": "legal_order_type",
							"choices": [
								[
									"SUBPOENA",
									"subpoena"
								],
								[
									"2703",
									"2703(d) court order"
								],
								[
									"WARRANT",
									"warrant"
								],
								[
									"NATIONAL_SECURITY_LETTER",
									"national security letter"
								],
								[
									"FISA",
									"FISA order"
								],
								[
									"OTHER",
									"other"
								]
							]
						}
					]
				},
				{
					"id": 11,
					"title": "Equipment Damage",
					"url": "/equipment-damage/",
					"symbol": "equipment_damage",
					"filters": [
						{
							"title": "Equipment Broken",
							"type": "autocomplete",
							"name": "equipment_broken",
							"autocomplete_type": "incident.Equipment",
							"choices": [
								"graph paper",
								"compass",
								"planimeter",
								"photometer",
								"protractor",
								"calculator",
								"timer",
								"abacus",
								"ruler",
								"hygrometer",
								"diffuser",
								"multimeter",
								"microscope"
							],
							"many": true
						}
					]
				},
				{
					"id": 12,
					"title": "Prior Restraint",
					"url": "/prior-restraint/",
					"symbol": "prior_restraint",
					"filters": [
						{
							"title": "Status of prior restraint",
							"type": "choice",
							"name": "status_of_prior_restraint",
							"choices": [
								[
									"PENDING",
									"pending"
								],
								[
									"DROPPED",
									"dropped"
								],
								[
									"STRUCK_DOWN",
									"struck down"
								],
								[
									"UPHELD",
									"upheld"
								],
								[
									"IGNORED",
									"ignored"
								]
							]
						}
					]
				},
				{
					"id": 13,
					"title": "Chilling Statement",
					"url": "/chilling-statement/",
					"symbol": "chilling_statement",
					"filters": []
				},
				{
					"id": 14,
					"title": "Other Incident",
					"url": "/other-incident/",
					"symbol": "other_incident",
					"filters": []
				}
			]}
		/>
	)).toMatchSnapshot();
});
