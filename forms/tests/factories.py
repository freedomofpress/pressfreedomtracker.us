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
        exclude = ('choices_text', 'placeholder_text')

    field_type = 'singleline'
    choices_text = Faker('words', nb=4)
    placeholder_text = Faker('sentence')
    sort_order = Sequence(int)
    label = Faker('sentence', nb_words=6, variable_nb_words=True)
    required = Faker('boolean', chance_of_getting_true=50)
    placeholder = LazyAttribute(lambda o: o.placeholder_text[:-1])
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
        exclude = ('title_words', )

    title_words = Faker('words', nb=4)

    title = LazyAttribute(lambda o: ' '.join(o.title_words).capitalize())
    description = Faker('sentence')
    sort_order = Sequence(int)
    template = 'default'


class SingleLineDateFieldGroupFactory(FieldGroupFactory):
    class Meta:
        model = FieldGroup

    template = 'date_single'
    day = RelatedFactory(
        FormFieldFactory,
        'group',
        label='Day',
        field_type='singleline',
        placeholder='DD',
    )
    month = RelatedFactory(
        FormFieldFactory,
        'group',
        label='Month',
        field_type='singleline',
        placeholder='MM',
    )
    year = RelatedFactory(
        FormFieldFactory,
        'group',
        label='Year',
        field_type='singleline',
        placeholder='YYYY',
    )


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
    form_intro = Faker('sentence')
    thank_you_text = Faker('sentence')
    outro_title = Faker('sentence')
    button_text = 'Submit Answers'

    field_group = RelatedFactory(FormPageFieldGroupFactory, 'page')
    field_group2 = RelatedFactory(SingleLineDateFieldGroupFactory, 'page')


class FormPageWithReplyToFieldFactory(PageFactory):
    class Meta:
        model = FormPage

    field_group = RelatedFactory(FormPageWithReplyToFieldFieldGroupFactory, 'page')


class FormPageWithAppendSubjectFieldsFactory(PageFactory):
    class Meta:
        model = FormPage

    field_group = RelatedFactory(FormPageWithAppendSubjectFieldsFieldGroupFactory, 'page')
