from inspect import Parameter
import inspect

from django.core.exceptions import ValidationError
from django.utils.text import smart_split
from wagtail.wagtailcore import blocks

from incident.utils.incident_filter import IncidentFilter
from statistics.registry import (
    get_stats_choices,
    get_visualization_choices,
    MAPS,
    NUMBERS,
    VISUALIZATIONS,
)
from statistics.utils import parse_kwargs
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
            fn = MAPS[dataset]
            if visualization.statistics_type == NUMBER:
                errors['dataset'] = ['A map dataset cannot be used with a number visualization']
        else:
            fn = NUMBERS[dataset]
            if visualization.statistics_type == MAP:
                errors['dataset'] = ['A number dataset cannot be used with a map visualization']

        params = list(smart_split(cleaned_value['params']))

        signature = inspect.signature(fn)
        has_kwargs = any(param.kind == Parameter.VAR_KEYWORD for param in signature.parameters.values())

        if has_kwargs:
            try:
                data = parse_kwargs(params)
            except ValueError as exc:
                errors['params'] = [str(exc)]
            else:
                incident_filter = IncidentFilter(data)
                try:
                    incident_filter.clean(strict=True)
                except ValidationError as exc:
                    errors['params'] = [str(error) for error in exc]
        else:
            positional_keyword_params = [
                param
                for param in signature.parameters.values()
                if param.kind == Parameter.POSITIONAL_OR_KEYWORD
            ]
            required_params = [
                param
                for param in positional_keyword_params
                if param.default == Parameter.empty
            ]
            param_count = len(params)
            min_param_count = len(required_params)
            max_param_count = len(positional_keyword_params)

            if param_count < min_param_count:
                errors['params'] = ['At least {} parameter{} must be supplied for this dataset'.format(min_param_count, 's' if min_param_count != 1 else '')]

            if param_count > max_param_count:
                if max_param_count == 0:
                    errors['params'] = ['No parameters may be supplied for this dataset']
                else:
                    errors['params'] = ['At most {} parameter{} may be supplied for this dataset'.format(max_param_count, 's' if max_param_count != 1 else '')]

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
