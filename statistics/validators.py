from inspect import Parameter
import inspect

from django.core.exceptions import ValidationError
from django.utils.text import smart_split

from statistics.registry import (
    MAPS,
    NUMBERS,
)
from statistics.utils import parse_kwargs


def validate_dataset_params(dataset, params):
    from incident.utils.incident_filter import IncidentFilter

    errors = {}

    if dataset in MAPS:
        fn = MAPS[dataset]
    elif dataset in NUMBERS:
        fn = NUMBERS[dataset]
    else:
        raise ValidationError(f'Dataset {dataset!r} not found')

    params = list(smart_split(params))

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
        raise ValidationError(errors)
