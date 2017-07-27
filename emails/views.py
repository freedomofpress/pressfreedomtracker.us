from django.db import IntegrityError
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
        EmailSignup.objects.create(email_address=email_address)
    except IntegrityError:
        return HttpResponseBadRequest('already_signed_up')
    except:
        return HttpResponseBadRequest()

    return HttpResponse('success')
