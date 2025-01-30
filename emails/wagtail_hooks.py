from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from emails.models import EmailSignup


class EmailSignupSnippetViewSet(SnippetViewSet):
    model = EmailSignup
    add_to_admin_menu = True
    list_display = (
        'id',
        'email_address',
        'signup_time',
    )


register_snippet(EmailSignupSnippetViewSet)
