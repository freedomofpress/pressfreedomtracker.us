from factory import (
    DjangoModelFactory,
    Faker,
    RelatedFactory,
    LazyAttribute,
    Trait,
    Sequence,
)
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
