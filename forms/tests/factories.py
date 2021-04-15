from factory import (
    Faker,
    RelatedFactory,
    LazyAttribute,
    Trait,
    Sequence,
)
from factory.django import DjangoModelFactory
from wagtail_factories import PageFactory

from forms.models import FormField, FormPage


class FormFieldFactory(DjangoModelFactory):
    class Meta:
        model = FormField
        exclude = ('choices_text',)

    field_type = 'singleline'
    choices_text = Faker('words', nb=4)
    sort_order = Sequence(int)
    label = Faker('sentence', nb_words=6, variable_nb_words=True)
    required = Faker('boolean', chance_of_getting_true=50)
    use_as_reply_to = False

    class Params:
        radio = Trait(
            field_type='radio',
            choices=LazyAttribute(lambda o: ','.join(o.choices_text)),
        )
        checkboxes = Trait(
            field_type='checkboxes',
            choices=LazyAttribute(lambda o: ','.join(o.choices_text)),
        )
        dropdown = Trait(
            field_type='dropdown',
            choices=LazyAttribute(lambda o: ','.join(o.choices_text)),
        )


class FormPageFactory(PageFactory):
    class Meta:
        model = FormPage

    intro = Faker('sentence')
    thank_you_text = Faker('sentence')
    button_text = 'Submit'

    singleline_field = RelatedFactory(FormFieldFactory, 'page')
    multiline_field = RelatedFactory(FormFieldFactory, 'page', field_type='multiline')
    email_field = RelatedFactory(FormFieldFactory, 'page', field_type='email')
    number_field = RelatedFactory(FormFieldFactory, 'page', field_type='number')
    url_field = RelatedFactory(FormFieldFactory, 'page', field_type='url')
    checkbox_field = RelatedFactory(FormFieldFactory, 'page', field_type='checkbox')
    date_field = RelatedFactory(FormFieldFactory, 'page', field_type='date')
    datetime_field = RelatedFactory(FormFieldFactory, 'page', field_type='datetime')
    radio_field = RelatedFactory(FormFieldFactory, 'page', radio=True)
    dropdown_field = RelatedFactory(FormFieldFactory, 'page', dropdown=True)
    checkboxes_field = RelatedFactory(FormFieldFactory, 'page', checkboxes=True)


class FormPageWithReplyToFieldFactory(PageFactory):
    class Meta:
        model = FormPage

    email_field = RelatedFactory(
        FormFieldFactory,
        'page',
        field_type='email',
        use_as_reply_to=True,
        required=True,
        label='email_address',
    )


class FormPageWithAppendSubjectFieldsFactory(PageFactory):
    class Meta:
        model = FormPage

    subject_field = RelatedFactory(
        FormFieldFactory,
        'page',
        field_type='singleline',
        append_to_subject=True,
        required=True,
        label='topic',
    )

    subject_field2 = RelatedFactory(
        FormFieldFactory,
        'page',
        field_type='singleline',
        append_to_subject=True,
        required=True,
        label='theme',
    )
