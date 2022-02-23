from factory import (
    Faker,
    RelatedFactory,
    LazyAttribute,
    Trait,
    Sequence,
)
from factory.django import DjangoModelFactory
from wagtail_factories import PageFactory

from forms.models import GroupedFormField, FieldGroup, FormPage


class FormFieldFactory(DjangoModelFactory):
    class Meta:
        model = GroupedFormField
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


class FieldGroupFactory(DjangoModelFactory):
    class Meta:
        model = FieldGroup

    title = Faker('words', nb=4)
    description = Faker('sentence')
    sort_order = Sequence(int)
    template = 'text'


class FormPageFieldGroupFactory(FieldGroupFactory):
    class Meta:
        model = FieldGroup

    singleline_field = RelatedFactory(FormFieldFactory, 'group')
    multiline_field = RelatedFactory(FormFieldFactory, 'group', field_type='multiline')
    email_field = RelatedFactory(FormFieldFactory, 'group', field_type='email')
    number_field = RelatedFactory(FormFieldFactory, 'group', field_type='number')
    url_field = RelatedFactory(FormFieldFactory, 'group', field_type='url')
    checkbox_field = RelatedFactory(FormFieldFactory, 'group', field_type='checkbox')
    date_field = RelatedFactory(FormFieldFactory, 'group', field_type='date')
    datetime_field = RelatedFactory(FormFieldFactory, 'group', field_type='datetime')
    radio_field = RelatedFactory(FormFieldFactory, 'group', radio=True)
    dropdown_field = RelatedFactory(FormFieldFactory, 'group', dropdown=True)
    checkboxes_field = RelatedFactory(FormFieldFactory, 'group', checkboxes=True)


class FormPageWithReplyToFieldFieldGroupFactory(FieldGroupFactory):
    class Meta:
        model = FieldGroup

    email_field = RelatedFactory(
        FormFieldFactory,
        'group',
        field_type='email',
        use_as_reply_to=True,
        required=True,
        label='email_address',
    )


class FormPageWithAppendSubjectFieldsFieldGroupFactory(FieldGroupFactory):
    class Meta:
        model = FieldGroup

    subject_field = RelatedFactory(
        FormFieldFactory,
        'group',
        field_type='singleline',
        append_to_subject=True,
        required=True,
        label='topic',
    )

    subject_field2 = RelatedFactory(
        FormFieldFactory,
        'group',
        field_type='singleline',
        append_to_subject=True,
        required=True,
        label='theme',
    )


class FormPageFactory(PageFactory):
    class Meta:
        model = FormPage

    intro = Faker('sentence')
    thank_you_text = Faker('sentence')
    button_text = 'Submit'

    field_group = RelatedFactory(FormPageFieldGroupFactory, 'page')


class FormPageWithReplyToFieldFactory(PageFactory):
    class Meta:
        model = FormPage

    field_group = RelatedFactory(FormPageWithReplyToFieldFieldGroupFactory, 'page')


class FormPageWithAppendSubjectFieldsFactory(PageFactory):
    class Meta:
        model = FormPage

    field_group = RelatedFactory(FormPageWithAppendSubjectFieldsFieldGroupFactory, 'page')
