from marshmallow import Schema, fields


class BaseChartOptionsSchema(Schema):
    """Base schema that consolidates data shared between the options
    of different types of charts."""

    tag = fields.Str(attribute="incident_set.tag", data_key="filterTags")
    filter_categories = fields.List(
        fields.Str(),
        data_key="filterCategories",
        attribute="incident_set.categories",
    )
    date_range = fields.Method("get_date_range", data_key="dateRange")
    width = fields.Int()
    height = fields.Int()
    states = fields.List(
        fields.Str(),
        data_key="filterStates",
        attribute="incident_set.states",
    )

    def get_date_range(self, obj):
        lower = obj.get("incident_set", {}).get("lower_date", None)
        upper = obj.get("incident_set", {}).get("upper_date", None)
        if lower:
            lower = lower.isoformat()

        if upper:
            upper = upper.isoformat()
        return [lower, upper]


class VerticalBarChartOptionsSchema(BaseChartOptionsSchema):
    branch_field_name = fields.Function(
        lambda obj: obj.branch_field_name(), data_key="branchFieldName"
    )
    branches = fields.Function(lambda obj: obj.branches())
    group_by_tag = fields.Str(data_key="groupByTag")
    time_period = fields.Str(data_key="timePeriod")


class BubbleMapChartOptionsSchema(BaseChartOptionsSchema):
    group_by = fields.Str(data_key="aggregationLocality")


class HexbinMapChartOptionsSchema(BaseChartOptionsSchema):
    group_by = fields.Str(data_key="aggregationLocality")


class TreeMapOptionsSchema(BaseChartOptionsSchema):
    branch_field_name = fields.Function(
        lambda obj: obj.branch_field_name(), data_key="branchFieldName"
    )
    branches = fields.Function(lambda obj: obj.branches())
