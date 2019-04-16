import html
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
            raise ValueError("Invalid param formatting: '{}'".format(bit))

        key, value = match.groups()
        if key in kwargs:
            # The keyword argument has already been supplied once
            raise ValueError(
                "Received multiple values for param '{}'".format(key)
            )

        try:
            kwargs[key] = Variable(value).resolve({})
        except VariableDoesNotExist:
            raise ValueError("Value for {} should be wrapped in quotation marks".format(
                key,
            ))

    return kwargs


def unescape(content):
    """Unescape HTML entities within template block tag delimiters

    Example: the string
    `&quot;Hello {% num_incidents categories=&#x27;1&#x27; %} worlds&quot;`
    becomes
    `&quot;Hello {% num_incidents categories='1'; %} worlds!&quot;`
    """
    tag_re = re.compile('({%.*?%})')
    body = ''
    position = 0
    for match in tag_re.finditer(content):
        start, end = match.span()
        body += content[position:start]
        body += html.unescape(content[start:end])
        position = end
    body += content[position:len(content)]
    return body
