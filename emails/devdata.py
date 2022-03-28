import factory

from .models import EmailSettings, MailchimpGroup


class MailchimpGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MailchimpGroup

    category_id = 0
    group_id = 0


class EmailSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailSettings

    mailchimp_collect_name = True
    group1 = factory.RelatedFactory(MailchimpGroupFactory, 'page')
