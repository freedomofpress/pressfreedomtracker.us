import html
import re


def unescape(content):
    """Unescape HTML entities within template block tag delimiters

    Example: the string
    `&quot;Hello {% num_incidents categories=&#x27;1&#x27; %} worlds&quot;`
    becomes
    `&quot;Hello {% num_incidents categories='1' %} worlds!&quot;`
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
