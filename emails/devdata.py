import factory

from .models import EmailSettings, MailchimpGroup


class MailchimpGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MailchimpGroup

    audience_id = 'Audience_1'
    group_id = 'Group_1'


class EmailSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailSettings

    mailchimp_collect_name = True
    group1 = factory.RelatedFactory(MailchimpGroupFactory, 'page')
