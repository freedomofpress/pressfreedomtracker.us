from django.template.loader import render_to_string

from incident import choices


def basic_html_val(page, field, index, category):
    # If no value for the attribute, return blank
    value = getattr(page, field)
    if not value:
        return ''

    # If has a get_display function associated with the field, use that
    # else use just the field value
    display_value = value
    if hasattr(page, f'get_{field}_display'):
        display_value = getattr(page, 'get_{}_display'.format(field))()

    return render_to_string('incident/category_field/_basic_field.html', {
        'page': page,
        'field': field,
        'value': value,
        'display_value': display_value,
        'index': index,
        'category': category.title,
    })


def boolean_html_val(page, field, index, category):
    value = getattr(page, field, index)
    display_value = 'Yes' if value else 'No'

    return render_to_string('incident/category_field/_basic_field.html', {
        'page': page,
        'field': field,
        'index': index,
        'value': '1' if value else '0',
        'display_value': display_value
    })


def list_html_val(page, field, index, category):
    # If no value for the attribute, return blank
    items = getattr(page, field).all()
    if not items:
        return ''

    return render_to_string('incident/category_field/_list_field.html', {
        'page': page,
        'index': index,
        'field': field,
        'items': items,
    })


def equipments_list_html_val(page, field, index, category):
    # If no value for the attribute, return blank
    items = getattr(page, field).all()
    if not items:
        return ''

    return render_to_string('incident/category_field/_equipment_list_field.html', {
        'page': page,
        'index': index,
        'field': field,
        'items': items,
    })


def date_html_val(page, field, index, category):
    # If no value for the attribute, return blank
    value = getattr(page, field)
    if not value:
        return ''

    return render_to_string('incident/category_field/_date_field.html', {
        'page': page,
        'index': index,
        'field': field,
        'value': value,
    })


# Handle all the different category fields html values individually
# since a lot of them small small differences that can't all be
# covered using the generic functions above


def arrest_status_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def status_of_charges_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def arresting_authority_html_val(page, field, index, category):
    # If no value for the attribute, return blank
    if not getattr(page, field):
        return ''

    link = '{}?{}={}'.format(
        index.get_url(),
        field,
        getattr(page, field).title
    )
    value = getattr(page, field).title

    return f'<a href="{link}" class="text-link">{value}</a>'


def legal_orders_html_val(page, field, index, category):
    # If no value for the attribute, return blank
    items = getattr(page, field).all()
    if not items:
        return ''

    return render_to_string('incident/category_field/_legal_order_list_field.html', {
        'page': page,
        'index': index,
        'field': field,
        'items': items,
    })


def charges_html_val(page, field, index, category):
    # If no value for the attribute, return blank
    items = getattr(page, field).all()
    if not items:
        return ''

    return render_to_string('incident/category_field/_charge_list_field.html', {
        'page': page,
        'index': index,
        'field': field,
        'items': items,
    })


def detention_date_html_val(page, field, index, category):
    return date_html_val(page, field, index, category)


def release_date_html_val(page, field, index, category):
    return date_html_val(page, field, index, category)


def unnecessary_use_of_force_html_val(page, field, index, category):
    return boolean_html_val(page, field, index, category)


def equipment_broken_html_val(page, field, index, category):
    return equipments_list_html_val(page, field, index, category)


def equipment_seized_html_val(page, field, index, category):
    return equipments_list_html_val(page, field, index, category)


def status_of_seized_equipment_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def is_search_warrant_obtained_html_val(page, field, index, category):
    return boolean_html_val(page, field, index, category)


def actor_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def border_point_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def target_nationality_html_val(page, field, index, category):
    return list_html_val(page, field, index, category)


def target_us_citizenship_status_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def denial_of_entry_html_val(page, field, index, category):
    return boolean_html_val(page, field, index, category)


def stopped_previously_html_val(page, field, index, category):
    return boolean_html_val(page, field, index, category)


def did_authorities_ask_for_device_access_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def did_authorities_ask_about_work_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def assailant_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def was_journalist_targeted_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def workers_whose_communications_were_obtained_html_val(page, field, index, category):
    return list_html_val(page, field, index, category)


def charged_under_espionage_act_html_val(page, field, index, category):
    return boolean_html_val(page, field, index, category)


def subpoena_type_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def subpoena_statuses_html_val(page, field, index, category):
    if not getattr(page, field, index):
        return ''

    html = []
    for subpoena_status in getattr(page, field):
        link = '{}?{}={}'.format(
            index.get_url(),
            field,
            subpoena_status
        )
        value = dict(choices.SUBPOENA_STATUS).get(subpoena_status).capitalize()
        html.append(f'<a href="{link}" class="text-link">{value}</a>')
    html = ', '.join(html)
    return html


def type_of_denial_html_val(page, field, index, category):
    if not getattr(page, field, index):
        return ''

    html = []
    for type_of_denial in getattr(page, field):
        link = '{}?{}={}'.format(
            index.get_url(),
            field,
            type_of_denial,
        )
        value = choices.TypeOfDenial(type_of_denial).label
        html.append(f'<a href="{link}" class="text-link">{value}</a>')
    html = ', '.join(html)
    return html


def name_of_business_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def third_party_business_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def legal_order_type_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def legal_order_venue_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def status_of_prior_restraint_html_val(page, field, index, category):
    return basic_html_val(page, field, index, category)


def politicians_or_public_figures_involved_html_val(page, field, index, category):
    return list_html_val(page, field, index, category)


def legal_order_target_html_val(page, field, index, category):
    target = page.legal_order_target
    if not target:
        return ''
    if target in (choices.LegalOrderTarget.JOURNALIST, choices.LegalOrderTarget.INSTITUTION):
        return basic_html_val(page, field, index, category)
    elif target == choices.LegalOrderTarget.THIRD_PARTY:
        return render_to_string(
            'incident/category_field/_legal_order_target_third_party.html',
            {
                'page': page,
                'index': index,
                'target': target,

                'third_party_business': page.third_party_business,
                'category': category.title,
                # 'field': field,
                # 'items': items,
            }
        )
