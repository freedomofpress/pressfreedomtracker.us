from wagtail.wagtailcore import blocks

from statistics.registry import get_stats, get_stats_choices


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

    def get_context(self, value, parent_context=None):
        context = super(StatisticsBlock, self).get_context(value, parent_context=parent_context)
        fn = get_stats()[value['dataset']]

        if value.get('params'):
            result = fn(*value['params'].split())
        else:
            result = fn()
        context['data'] = result
        return context

    class Meta:
        template = 'stats.html'
        icon = 'cogs'
        label = 'Statistics'
