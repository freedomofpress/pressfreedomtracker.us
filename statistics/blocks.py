from django.core.exceptions import ValidationError
from wagtail.wagtailcore import blocks

from statistics.registry import (
    get_stats_choices,
    get_visualization_choices,
    MAPS,
    VISUALIZATIONS,
)
from statistics.validators import validate_dataset_params
from statistics.visualizations import MAP, NUMBER


class StatisticsBlock(blocks.StructBlock):
    visualization = blocks.ChoiceBlock(
        choices=get_visualization_choices,
    )
    dataset = blocks.ChoiceBlock(
        choices=get_stats_choices,
    )
    params = blocks.CharBlock(
        required=False,
        help_text='Whitespace-separated list of arguments to be passed to the statistics function',
    )

    def clean(self, value):
        cleaned_value = super(StatisticsBlock, self).clean(value)
        errors = {}

        visualization = VISUALIZATIONS[cleaned_value['visualization']]
        dataset = cleaned_value['dataset']

        if dataset in MAPS:
            if visualization.statistics_type == NUMBER:
                errors['dataset'] = ['A map dataset cannot be used with a number visualization']
        else:
            if visualization.statistics_type == MAP:
                errors['dataset'] = ['A number dataset cannot be used with a map visualization']

        try:
            validate_dataset_params(dataset, cleaned_value['params'])
        except ValidationError as exc:
            errors.update({
                key: [str(error) for error in errors]
                for key, errors in exc
            })

        if errors:
            # The message here is arbitrary - StructBlock.render_form will suppress it
            # and delegate the errors contained in the 'params' dict to the child blocks instead
            # See wagtail/wagtailcore/blocks/struct_block.py line 116
            raise ValidationError('Validation error in StructBlock', params=errors)

        return cleaned_value

    def get_context(self, value, parent_context=None):
        context = super(StatisticsBlock, self).get_context(value, parent_context=parent_context)

        template_string = '{{% {tag_name}{params} as data %}}{{% include "{visualization}" %}}'.format(
            tag_name=value['dataset'],
            params=' ' + value['params'] if value['params'] else '',
            visualization=value['visualization'],
        )
        context['template_string'] = template_string
        return context

    class Meta:
        template = 'statistics/blocks/stats.html'
        icon = 'cogs'
        label = 'Statistics'
