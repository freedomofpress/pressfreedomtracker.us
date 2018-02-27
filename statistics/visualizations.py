from statistics.registry import Statistics


statistics = Statistics()


NUMBER = 'number'
MAP = 'map'


@statistics.visualization
class BigNumberBox(object):
    verbose_name = 'Big Number Box'
    template_name = 'statistics/visualizations/big-number.html'
    statistics_type = NUMBER


@statistics.visualization
class BigBlueTable(object):
    verbose_name = 'Big Blue Table'
    template_name = 'statistics/visualizations/blue-table.html'
    statistics_type = MAP


@statistics.visualization
class OrangeTable(object):
    verbose_name = 'Orange Table'
    template_name = 'statistics/visualizations/orange-table.html'
    statistics_type = MAP
