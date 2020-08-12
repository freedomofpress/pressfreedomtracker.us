from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.mail import get_connection


def send_mail(subject, message, recipient_list, from_email=None, **kwargs):
    """Modified clone of wagtail.admin.utils.send_mail that allows
    modifying the Reply-To header.

    """
    if not from_email:
        if hasattr(settings, 'WAGTAILADMIN_NOTIFICATION_FROM_EMAIL'):
            from_email = settings.WAGTAILADMIN_NOTIFICATION_FROM_EMAIL
        elif hasattr(settings, 'DEFAULT_FROM_EMAIL'):
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = 'webmaster@localhost'

    connection = kwargs.get('connection', False) or get_connection(
        username=kwargs.get('auth_user', None),
        password=kwargs.get('auth_password', None),
        fail_silently=kwargs.get('fail_silently', None),
    )
    multi_alt_kwargs = {
        'connection': connection,
        'reply_to': kwargs.get('reply_to', None),
        'headers': {
            'Auto-Submitted': 'auto-generated',
        }
    }
    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, **multi_alt_kwargs)
    html_message = kwargs.get('html_message', None)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()
