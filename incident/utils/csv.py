import typing
import dataclasses
import itertools
from datetime import date
from urllib.parse import urlparse

from incident.models import (
    IncidentPage,
    choices,
)


class LegalOrderInfo:
    legal_order_type: choices.LegalOrderType


class CsvError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.column_name = kwargs.get('column_name')


class ChoiceNotFound(CsvError):
    pass


class ColumnNotFound(CsvError):
    pass


@dataclasses.dataclass
class Result:
    def __init__(self, success, value, errors):
        self.success = success
        self.value = value
        self.errors = errors

    @classmethod
    def fail(cls, errors):
        return cls(False, None, errors=errors)

    @classmethod
    def ok(cls, value):
        return cls(True, value, errors=[])

    def join(self, other):
        if self.success:
            if other.success:
                # Merge the two dictionaries
                return Result.ok(dict(self.value, **other.value))
            else:
                return Result.fail(other.errors)
        else:
            if other.success:
                return self
            else:
                return Result.fail(self.errors + other.errors)


@dataclasses.dataclass
class CsvDataProblem:
    message: str
    column_name: str


class ColumnSet:
    def __init__(self, specs):
        self.specs = specs
        self.errors = []
        self.data = {}

    def evaluate(self, row, column_prefix=None, column_suffix=None):
        result = Result.ok({})
        for spec in self.specs:
            try:
                result = result.join(
                    spec.get_value(row, column_prefix, column_suffix)
                )
            except CsvError as err:
                result = result.join(
                    Result.fail([
                        CsvDataProblem(message=err, column_name=err.column_name)
                    ])
                )

        return result


class DateColumn:
    def __init__(self, name):
        self.name = name

    def get_value(self, row, prefix=None, suffix=None):
        key = self.name
        if prefix:
            key = f'{prefix}{key}'
        if suffix:
            key = f'{key}{suffix}'
        try:
            row_value = row[key]
        except KeyError:
            raise ColumnNotFound('Column not found', column_name=key)

        try:
            # We return a string since we are ultimately serializing
            # this value as JSON.
            formatted_date = date.fromisoformat(row_value).isoformat()
            return Result.ok(formatted_date)
        except ValueError as err:
            return Result.fail([
                CsvDataProblem(message=err, column_name=key)
            ])


class ChoiceColumn:
    def __init__(self, name, choice_type):
        self.name = name
        self.choice_type = choice_type

    def get_value(self, row, prefix=None, suffix=None):
        key = self.name
        if prefix:
            key = f'{prefix}{key}'
        if suffix:
            key = f'{key}{suffix}'
        try:
            row_value = row[key]
        except KeyError:
            raise ColumnNotFound('Column not found', column_name=key)

        for value, label in self.choice_type.choices:
            if label.casefold() == row_value.casefold():
                return Result.ok(self.choice_type(value))
        legal_choices = ', '.join(self.choice_type.labels)
        raise ChoiceNotFound(
            f'{row_value} is invalid input for {self.choice_type}, choices are: {legal_choices}',
            column_name=key,
        )


class EnumeratedColumns:
    def __init__(
            self,
            prefix_format: typing.Optional[str],
            suffix_format: typing.Optional[str],
            column_set: ColumnSet,
    ):
        self.prefix_format = prefix_format
        self.suffix_format = suffix_format
        self.column_set = column_set

    def get_value(self, row, column_prefix=None, column_suffix=None):
        value = []
        all_errors = []

        for i in itertools.count(1):
            prefix = (
                column_prefix if column_prefix else '' +
                self.prefix_format if self.prefix_format else ''
            ).format(
                i=i,
            )

            suffix = (self.suffix_format if self.suffix_format else '').format(
                i=i,
            )

            # Only consider columns beginning with the sequence prefix
            # or ending with its suffix.  If there are none, the
            # sequence is considered finished and we can return.
            row_subset = row
            if self.suffix_format:
                row_subset = {
                    k: v for k, v in row_subset.items() if k.endswith(suffix)
                }
            if self.prefix_format:
                row_subset = {
                    k: v for k, v in row_subset.items() if k.startswith(prefix)
                }
            # Only consider rows with nonempty values
            row_subset = {
                k: v for k, v in row_subset.items() if v
            }
            if not row_subset:
                break

            result = self.column_set.evaluate(row_subset, prefix, suffix)

            if result.success:
                value.append(result.value)
            else:
                all_errors.extend(result.errors)
        if all_errors:
            return Result.fail(all_errors)
        else:
            return Result.ok(value)


@dataclasses.dataclass
class ColumnSpec:
    key: str
    column: typing.Union[ChoiceColumn, EnumeratedColumns, DateColumn]

    def get_value(self, row, prefix, suffix):
        result = self.column.get_value(row, prefix, suffix)
        if result.success:
            return Result.ok({self.key: result.value})
        else:
            return result


def parse_row(row):
    result = Result.ok({})

    cset = ColumnSet(
        specs=[
            ColumnSpec('venue', ChoiceColumn('venue', choices.LegalOrderVenue)),
            ColumnSpec('target', ChoiceColumn('target', choices.LegalOrderTarget)),
            ColumnSpec(
                'legal_orders',
                EnumeratedColumns(
                    prefix_format='legal_order{i}_',
                    suffix_format=None,
                    column_set=ColumnSet([
                        ColumnSpec('type', ChoiceColumn('type', choices.LegalOrderType)),
                        ColumnSpec(
                            'information_requested',
                            ChoiceColumn(
                                'information_requested',
                                choices.InformationRequested,
                            ),
                        ),
                        ColumnSpec('statuses', EnumeratedColumns(
                            column_set=ColumnSet([
                                ColumnSpec('status', ChoiceColumn('status', choices.LegalOrderStatus)),
                                ColumnSpec('date', DateColumn('date')),
                            ]),
                            prefix_format=None,  # no prefix for these
                            suffix_format='{i}',
                        ))
                    ])
                )
            )
        ]
    )

    slug = urlparse(row['slug']).path.strip('/').split('/')[-1]
    try:
        incident = IncidentPage.objects.get(slug=slug)
    except IncidentPage.DoesNotExist:
        result = result.join(
            Result.fail([
                CsvDataProblem(
                    message=f'Could not locate incident at {row["slug"]}',
                    column_name='slug',
                )
            ])
        )
    result = result.join(cset.evaluate(row))
    if result.success:
        return Result.ok({incident.pk: result.value})
    else:
        return result
