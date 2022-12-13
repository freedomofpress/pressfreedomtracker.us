from django.utils.html import format_html
from wagtail import hooks


@hooks.register('insert_editor_css')
def global_admin_css():
    return format_html(
        """
        <style>

            .nested-inline .fields label {{
                display: block;
                float: none;
                width: 100%;
                padding-top: 0;
            }}

            .nested-inline input[name$='clean_name'] {{
                display: none;
            }}

            .full-width .multiple,
            .full-width .field-content {{
                width: 100%;
                max-width: none;
            }}

        </style>
        """
    )
