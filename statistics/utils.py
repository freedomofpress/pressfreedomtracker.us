import re

from django.template import Variable, VariableDoesNotExist


kwarg_re = re.compile(r"^(\w+)=(.+)$")


def parse_kwargs(bits):
    """
    Given a list of k=v strings, parses them into keyword arguments.
    """
    kwargs = {}

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise ValueError(f"Invalid param formatting: '{bit}'")

        key, value = match.groups()
        if key in kwargs:
            # The keyword argument has already been supplied once
            raise ValueError(f"Received multiple values for param '{key}'")

        try:
            kwargs[key] = Variable(value).resolve({})
        except VariableDoesNotExist:
            raise ValueError(
                f"Value for {key} should be wrapped in quotation marks"
            )

    return kwargs
