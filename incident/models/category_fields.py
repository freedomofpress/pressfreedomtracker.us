from incident.utils.category_field_values import (
    arrest_status_html_val,
    status_of_charges_html_val,
    arresting_authority_html_val,
    charges_html_val,
    detention_date_html_val,
    release_date_html_val,
    unnecessary_use_of_force_html_val,
    equipment_broken_html_val,
    equipment_seized_html_val,
    status_of_seized_equipment_html_val,
    is_search_warrant_obtained_html_val,
    actor_html_val,
    border_point_html_val,
    target_nationality_html_val,
    target_us_citizenship_status_html_val,
    denial_of_entry_html_val,
    stopped_previously_html_val,
    did_authorities_ask_for_device_access_html_val,
    did_authorities_ask_about_work_html_val,
    assailant_html_val,
    was_journalist_targeted_html_val,
    workers_whose_communications_were_obtained_html_val,
    charged_under_espionage_act_html_val,
    subpoena_type_html_val,
    subpoena_statuses_html_val,
    name_of_business_html_val,
    third_party_business_html_val,
    legal_order_type_html_val,
    status_of_prior_restraint_html_val,
    mistakenly_released_materials_html_val,
    politicians_or_public_figures_involved_html_val,
    legal_orders_html_val,
    legal_order_target_html_val,
    legal_order_venue_html_val,
    type_of_denial_html_val,
)

CATEGORY_FIELD_MAP = {
    'arrest-criminal-charge': [
        ('arrest_status', 'Arrest Status'),
        ('arresting_authority', 'Arresting Authority'),
        ('charges', 'Charges'),
        ('detention_date', 'Detention Date'),
        ('release_date', 'Release Date'),
        ('unnecessary_use_of_force', 'Unnecessary use of force?'),
    ],
    'equipment-damage': [
        ('equipment_broken', 'Equipment Broken'),
        ('actor', 'Actor'),
    ],
    'equipment-search-seizure-or-damage': [
        ('equipment_seized', 'Equipment Seized'),
        ('status_of_seized_equipment', 'Status of Seized Equipment'),
        ('is_search_warrant_obtained', 'Search Warrant Obtained'),
    ],
    'border-stop': [
        ('border_point', 'Border Point'),
        ('target_nationality', 'Target Nationality'),
        ('target_us_citizenship_status', 'US Citizenship Status of Target'),
        ('denial_of_entry', 'Denied Entry?'),
        ('stopped_previously', 'Stopped Previously?'),
        ('did_authorities_ask_for_device_access', 'Asked for device access?'),
        ('did_authorities_ask_about_work', 'Asked intrusive questions about work?'),
    ],
    'assault': [
        ('assailant', 'Assailant'),
        ('was_journalist_targeted', 'Was the journalist targeted?'),
    ],
    'leak-case': [
        ('workers_whose_communications_were_obtained', 'Alleged Recipient of Leak'),
        ('charged_under_espionage_act', 'Charged under Espionage Act'),
    ],
    'subpoena': [
        ('legal_orders', 'Legal Orders'),
        ('legal_order_target', 'Legal Order Target'),
        ('legal_order_venue', 'Legal Order Venue'),
    ],
    'prior-restraint': [
        ('status_of_prior_restraint', 'Status of Prior Restraint'),
        ('mistakenly_released_materials', 'Mistakenly Released Materials?'),
    ],
    'denial-access': [
        ('politicians_or_public_figures_involved', 'Government agency or public official involved'),
        ('type_of_denial', 'Type of denial'),
    ],
}

CAT_FIELD_VALUES = {
    'arrest_status': arrest_status_html_val,
    'status_of_charges': status_of_charges_html_val,
    'arresting_authority': arresting_authority_html_val,
    'charges': charges_html_val,
    'detention_date': detention_date_html_val,
    'release_date': release_date_html_val,
    'unnecessary_use_of_force': unnecessary_use_of_force_html_val,
    'equipment_broken': equipment_broken_html_val,
    'equipment_seized': equipment_seized_html_val,
    'status_of_seized_equipment': status_of_seized_equipment_html_val,
    'is_search_warrant_obtained': is_search_warrant_obtained_html_val,
    'actor': actor_html_val,
    'border_point': border_point_html_val,
    'target_nationality': target_nationality_html_val,
    'target_us_citizenship_status': target_us_citizenship_status_html_val,
    'denial_of_entry': denial_of_entry_html_val,
    'stopped_previously': stopped_previously_html_val,
    'did_authorities_ask_for_device_access': did_authorities_ask_for_device_access_html_val,
    'did_authorities_ask_about_work': did_authorities_ask_about_work_html_val,
    'assailant': assailant_html_val,
    'was_journalist_targeted': was_journalist_targeted_html_val,
    'workers_whose_communications_were_obtained': workers_whose_communications_were_obtained_html_val,
    'charged_under_espionage_act': charged_under_espionage_act_html_val,
    'subpoena_type': subpoena_type_html_val,
    'subpoena_statuses': subpoena_statuses_html_val,
    'name_of_business': name_of_business_html_val,
    'third_party_business': third_party_business_html_val,
    'legal_order_type': legal_order_type_html_val,
    'status_of_prior_restraint': status_of_prior_restraint_html_val,
    'mistakenly_released_materials': mistakenly_released_materials_html_val,
    'politicians_or_public_figures_involved': politicians_or_public_figures_involved_html_val,
    'type_of_denial': type_of_denial_html_val,
    'legal_orders': legal_orders_html_val,
    'legal_order_target': legal_order_target_html_val,
    'legal_order_venue': legal_order_venue_html_val,
}
