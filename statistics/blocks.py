from inspect import Parameter
import inspect

from django.core.exceptions import ValidationError
from wagtail.wagtailcore import blocks

from incident.utils.incident_filter import IncidentFilter
from statistics.registry import get_stats, get_stats_choices
from statistics.utils import parse_kwargs


def get_visualization_choices():
    # The first value of each of these pairs must be a file in the
    # statistics/templates folder.  The second value is a descriptive
    # name for the visualization.
    return [
        ('big-number.html', 'Big Number Box'),
        ('blue-table.html', 'Big Blue Table'),
        ('orange-table.html', 'Orange Table'),
    ]


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

        fn = get_stats()[cleaned_value['dataset']]
        params = cleaned_value['params'].split()

        signature = inspect.signature(fn)
        required_params = [param for param in signature.parameters.values() if param.default == Parameter.empty]
        has_kwargs = any(param.kind == Parameter.VAR_KEYWORD for param in signature.parameters.values())

        param_count = len(params)
        min_param_count = len(required_params)
        max_param_count = len(signature.parameters)

        if param_count < min_param_count:
            errors['params'] = ['At least {} parameter{} must be supplied for this dataset'.format(min_param_count, 's' if min_param_count != 1 else '')]

        if param_count > max_param_count:
            if max_param_count == 0:
                errors['params'] = ['No parameters may be supplied for this dataset']
            else:
                errors['params'] = ['At most {} parameter{} may be supplied for this dataset'.format(max_param_count, 's' if max_param_count != 1 else '')]

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

        if errors:
            # The message here is arbitrary - StructBlock.render_form will suppress it
            # and delegate the errors contained in the 'params' dict to the child blocks instead
            # See wagtail/wagtailcore/blocks/struct_block.py line 116
            raise ValidationError('Validation error in StructBlock', params=errors)

        return cleaned_value

    def get_context(self, value, parent_context=None):
        context = super(StatisticsBlock, self).get_context(value, parent_context=parent_context)
        fn = get_stats()[value['dataset']]

        try:
            result = fn(*value['params'].split())
        except TypeError:
            result = None

        context['data'] = result
        return context

    class Meta:
        template = 'stats.html'
        icon = 'cogs'
        label = 'Statistics'
