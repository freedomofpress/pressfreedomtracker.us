from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from emails.models import EmailSignup


@csrf_exempt
@require_POST
def email_signup_create(request):
    if 'email_address' not in request.POST:
        return HttpResponseBadRequest()
    email_address = request.POST.get('email_address')

    try:
        email = EmailSignup(email_address=email_address)
        email.full_clean()
        email.save()
    except ValidationError as error:
        message = error.message_dict.get('email_address')
        if len(message) > 0:
            message = message[0]
        if 'already exists' in message:
            return HttpResponseBadRequest('already_signed_up')
        else:
            return HttpResponseBadRequest(message)
    except Exception:
        return HttpResponseBadRequest()

    return HttpResponse('success')
