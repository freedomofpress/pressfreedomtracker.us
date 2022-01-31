from incident.models import choices

def basic_html_val(page, field):
    # If no value for the attribute, return blank
    if not getattr(page, field):
        return ''

    link = '{}?{}={}'.format(
        page.get_parent().get_url(),
        field,
        getattr(page, field)
    )

    # If has a get_display function associated with the field, use that
    # else use just the field value
    if hasattr(page, 'get_{}_display'.format(field)):
        value = getattr(page, 'get_{}_display'.format(field))().capitalize()
    else:
        value = getattr(page, field).capitalize()

    return '<a href="{}" class="text-link">{}</a>'.format(
        link,
        value
    )

def boolean_html_val(page, field):
    # If no value for the attribute, return blank
    if not getattr(page, field):
        return ''

    link = '{}?{}={}'.format(
        page.get_parent().get_url(),
        field,
        getattr(page, field)
    )
    value = 'Yes' if getattr(page, field) else 'No'

    return '<a href="{}" class="text-link">{}</a>'.format(
        link,
        value
    )

def list_html_val(page, field):
    # If no value for the attribute, return blank
    if not getattr(page, field):
        return ''

    val_list = []
    for item in getattr(page, field).all():
        link = '{}?{}={}'.format(
            page.get_parent().get_url(),
            field,
            item.pk
        )
        value = item.title.capitalize()
        val_list.append(
            '<li class="details-table__list-item"><a href="{}" class="text-link">{}</a></li>'.format(
            link,
            value
        ))

    return '<ul class="details-table__list">{}</ul>'.format('\n'.join(val_list))

def equipments_list_html_val(page, field):
    # If no value for the attribute, return blank
    if not getattr(page, field):
        return ''

    val_list = []
    for item in getattr(page, field).all():
        link = '{}?{}={}'.format(
            page.get_parent().get_url(),
            field,
            item.equipment.pk
        )
        value = '{}, {}'.format(item.equipment.name, item.quantity)
        val_list.append(
            '<li class="details-table__list-item"><a href="{}" class="text-link">{}</a></li>'.format(
            link,
            value
        ))

    return '<ul class="details-table__list">{}</ul>'.format('\n'.join(val_list))

def date_html_val(page, field):
    # If no value for the attribute, return blank
    if not getattr(page, field):
        return ''

    link = '{url}?{field}_lower={val}&{field}_upper={val}'.format(
        url=page.get_parent().get_url(),
        field=field,
        val=getattr(page, field).strftime('%Y-%m-%d')
    )
    value = getattr(page, field).strftime('%B %-d, %Y')

    return '<a href="{}" class="text-link"><time datetime="{}">{}</time></a>'.format(
        link,
        getattr(page, field).isoformat(),
        value
    )


# Handle all the different category fields html values individually
# since a lot of them small small differences that can't all be
# covered using the generic functions above

def arrest_status_html_val(page, field):
	return basic_html_val(page, field)

def status_of_charges_html_val(page, field):
	return basic_html_val(page, field)

def arresting_authority_html_val(page, field):
	# If no value for the attribute, return blank
    if not getattr(page, field):
        return ''

    link = '{}?{}={}'.format(
        page.get_parent().get_url(),
        field,
        getattr(page, field).pk
    )
    value = getattr(page, field).title.capitalize()

    return '<a href="{}" class="text-link">{}</a>'.format(
        link,
        value
    )

def current_charges_html_val(page, field):
	return list_html_val(page, field)

def dropped_charges_html_val(page, field):
	return list_html_val(page, field)

def detention_date_html_val(page, field):
	return date_html_val(page, field)

def release_date_html_val(page, field):
	return date_html_val(page, field)

def unnecessary_use_of_force_html_val(page, field):
	# If no value for the attribute and not main category, return blank
    main_category = page.get_main_category()
    if not getattr(page, field) and main_category.slug != 'arrest-detention':
        return ''

    link = '{}?{}={}&categories={}'.format(
        page.get_parent().get_url(),
        field,
        getattr(page, field),
        main_category.title
    )
    value = 'Yes' if getattr(page, field) else 'No'

    return '<a href="{}" class="text-link">{}</a>'.format(
        link,
        value
    )

def equipment_broken_html_val(page, field):
	return equipments_list_html_val(page, field)

def equipment_seized_html_val(page, field):
	return equipments_list_html_val(page, field)

def status_of_seized_equipment_html_val(page, field):
	return basic_html_val(page, field)

def is_search_warrant_obtained_html_val(page, field):
	return boolean_html_val(page, field)

def actor_html_val(page, field):
	return basic_html_val(page, field)

def border_point_html_val(page, field):
	return basic_html_val(page, field)

def target_nationality_html_val(page, field):
	return list_html_val(page, field)

def target_us_citizenship_status_html_val(page, field):
	return basic_html_val(page, field)

def denial_of_entry_html_val(page, field):
	return boolean_html_val(page, field)

def stopped_previously_html_val(page, field):
	return boolean_html_val(page, field)

def did_authorities_ask_for_device_access_html_val(page, field):
	return basic_html_val(page, field)

def did_authorities_ask_for_social_media_user_html_val(page, field):
	return basic_html_val(page, field)

def did_authorities_ask_for_social_media_pass_html_val(page, field):
	return basic_html_val(page, field)

def did_authorities_ask_about_work_html_val(page, field):
	return basic_html_val(page, field)

def assailant_html_val(page, field):
	return basic_html_val(page, field)

def was_journalist_targeted_html_val(page, field):
	return basic_html_val(page, field)

def workers_whose_communications_were_obtained_html_val(page, field):
	return list_html_val(page, field)

def charged_under_espionage_act_html_val(page, field):
	# If no value for the attribute and not main category, return blank
    main_category = page.get_main_category()
    if not getattr(page, field) and main_category.title != 'Leak Prosecutions':
        return ''

    if getattr(page, field):
        link = '{}?{}={}'.format(
            page.get_parent().get_url(),
            field,
            getattr(page, field)
        )
        value = 'Yes'
    else:
        link = '{}?{}={}&categories={}'.format(
            page.get_parent().get_url(),
            field,
            getattr(page, field),
            main_category.title
        )
        value = 'No'

    return '<a href="{}" class="text-link">{}</a>'.format(
        link,
        value
    )

def subpoena_type_html_val(page, field):
    return basic_html_val(page, field)

def subpoena_statuses_html_val(page, field):
    if not len(getattr(page, field)):
        return  ''

    html = []
    for subpoena_status in getattr(page, field):
        link = '{}?{}={}'.format(
            page.get_parent().get_url(),
            field,
            subpoena_status
        )
        value = dict(choices.SUBPOENA_STATUS).get(subpoena_status).capitalize()
        html.append('<a href="{}" class="text-link">{}</a>'.format(
            link,
            value
        ))
    html = ', '.join(html)
    return html

def held_in_contempt_html_val(page, field):
	return basic_html_val(page, field)

def detention_status_html_val(page, field):
	return basic_html_val(page, field)

def third_party_in_possession_of_communications_html_val(page, field):
	return basic_html_val(page, field)

def third_party_business_html_val(page, field):
	return basic_html_val(page, field)

def legal_order_type_html_val(page, field):
	return basic_html_val(page, field)

def status_of_prior_restraint_html_val(page, field):
	return basic_html_val(page, field)

def politicians_or_public_figures_involved_html_val(page, field):
	return list_html_val(page, field)


