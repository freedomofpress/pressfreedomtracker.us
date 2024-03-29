from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle

from emails.models import EmailSignup


class EmailSignupCreateUserThrottle(UserRateThrottle):
    rate = '20/hour'

    def get_ident(self, request):
        try:
            return request.headers["CF-Connecting-IP"]
        except KeyError:
            return super().get_ident(request)


@api_view(['POST'])
@throttle_classes([EmailSignupCreateUserThrottle])
def email_signup_create(request):
    if 'email_address' not in request.POST:
        return Response(status=400)
    email_address = request.POST.get('email_address')

    try:
        email = EmailSignup(email_address=email_address.strip())
        email.full_clean()
        email.save()
    except ValidationError as error:
        message = error.message_dict.get('email_address')
        if len(message) > 0:
            message = message[0]
        if 'already exists' in message:
            return Response('already_signed_up', status=400)
        else:
            return Response(status=400)
    except Exception:
        return Response(status=400)

    return Response('success', status=status.HTTP_200_OK)
