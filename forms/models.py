from django.db import models
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_control
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.core.models import Orderable
from wagtail.core.fields import RichTextField
from wagtail.contrib.forms.models import AbstractFormField
from wagtailcaptcha.models import WagtailCaptchaEmailForm

from forms.choices import FIELD_GROUP_TEMPLATE_CHOICES
from forms.email import send_mail
from common.models import MetadataPageMixin
from common.edit_handlers import HelpPanel


class ReplyToValidatorForm(WagtailAdminPageForm):
    def clean(self):
        cleaned_data = super().clean()

        reply_to_fields = []
        reply_to_forms = []
        for group in self.formsets['field_groups'].forms:
            for form in group.formsets['form_fields'].forms:
                if form.is_valid():
                    cleaned_form_data = form.clean()
                    reply_to_field = cleaned_form_data.get('use_as_reply_to')

                    if reply_to_field:
                        reply_to_fields.append(cleaned_form_data.get('label'))
                        reply_to_forms.append(form)

        if len(reply_to_fields) > 1:
            for form in reply_to_forms:
                form.add_error('use_as_reply_to', 'Only one field per form may have this option enabled.')
            raise ValidationError('Multiple fields with "Use as reply to" checked: {}'.format(', '.join(reply_to_fields)))

        return cleaned_data


class GroupedFormField(AbstractFormField):
    class Meta(AbstractFormField.Meta):
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(
                fields=['group'],
                condition=models.Q(use_as_reply_to=True),
                name='only_one_reply_to_form_field',
            )
        ]

    group = ParentalKey('FieldGroup', on_delete=models.CASCADE, related_name='form_fields')

    placeholder = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Optional: placeholder for the field',
    )
    append_to_subject = models.BooleanField(
        default=False,
        help_text='Add the contents of this field to the subject of the email sent by this from.  All fields with this checked will be appended.',
    )
    use_as_reply_to = models.BooleanField(
        default=False,
        help_text='Use the contents of this field as the Reply-To header of the email sent by this from.  Only one field per form can have this checked.',
    )

    panels = AbstractFormField.panels + [
        FieldPanel('placeholder'),
        FieldPanel('append_to_subject'),
        FieldPanel('use_as_reply_to'),
    ]


class FieldGroup(ClusterableModel, Orderable):
    class Meta:
        ordering = ['sort_order']
    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='field_groups')

    title = models.CharField(
        max_length=255,
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Optional: description for the field group',
    )
    template = models.CharField(
        max_length=20,
        choices=FIELD_GROUP_TEMPLATE_CHOICES,
        default=FIELD_GROUP_TEMPLATE_CHOICES[0][0],
        help_text='Select template used to display this field group',
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('template'),
        InlinePanel('form_fields', label="Form field", classname='full-width nested-inline'),
    ]

    @cached_property
    def fields(self):
        return self.form_fields.all()


@method_decorator(cache_control(private=True), name='serve')
class FormPage(MetadataPageMixin, WagtailCaptchaEmailForm):
    intro = RichTextField(blank=True)
    form_intro = models.TextField(
        blank=True,
        null=True,
        help_text='Optional: short intro for the form',
    )
    thank_you_text = RichTextField(blank=True)
    button_text = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    outro_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Optional: title for the page outro',
    )
    outro_text = RichTextField(
        blank=True,
        null=True,
        help_text='Optional: text for the page outro',
    )

    content_panels = [
        HelpPanel(heading='Note', content='Forms can be embedded in an iframe by a third-party website. '
                  'Append <code>?embed=t</code> to any FormPage URL to request the embeddable version. '
                  'You can copy the code below and replace <code>[[URL TO FORM]]</code> with the full link to this form page.'
                  '<textarea style="font-size: 1em; color: black; font-family: monospace; border: 0; padding: 0.5em">'
                  '<iframe src="[[URL TO FORM]]?embed=t" width="100%" height="60vh"></iframe>'
                  '</textarea>'),
    ] + WagtailCaptchaEmailForm.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('form_intro', classname="full"),
        InlinePanel('field_groups', label="Field group"),
        FieldPanel('thank_you_text', classname="full"),
        FieldPanel('button_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
        MultiFieldPanel([
            FieldPanel('outro_title'),
            FieldPanel('outro_text'),
        ], "Outro"),
    ]
    base_form_class = ReplyToValidatorForm

    @cached_property
    def groups(self):
        return self.field_groups.all()

    def get_form_fields(self):
        fields = []
        for group in self.field_groups.all():
            for field in group.form_fields.all():
                fields.append(field)

        return fields

    def get_context(self, request, *args, **kwargs):
        context = super(FormPage, self).get_context(request, *args, **kwargs)
        if request.GET.get('embed', None):
            context['template_name'] = 'base.chromeless.html'
        else:
            context['template_name'] = 'base.html'
        return context

    def serve(self, request, *args, **kwargs):
        response = super(FormPage, self).serve(request, *args, **kwargs)
        if 'embed' in request.GET:
            response.xframe_options_exempt = True
        return response

    def send_mail(self, form):
        fields = {x.clean_name: x for x in self.get_form_fields()}
        addresses = [x.strip() for x in self.to_address.split(',')]
        content = []
        reply_to = []
        subject = self.subject

        for field in form:
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            content.append('{}: {}'.format(field.label, value))

            if fields.get(field.name):
                if fields.get(field.name).append_to_subject and value:
                    subject = '{0} - {1}'.format(subject, field.value())
                if fields.get(field.name).use_as_reply_to and value:
                    reply_to = [value]
        content = '\n'.join(content)
        send_mail(subject, content, addresses, self.from_address, reply_to=reply_to)
