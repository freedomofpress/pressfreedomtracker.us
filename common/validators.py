from django.core.exceptions import ValidationError
from django.template.base import Parser, Lexer
from django.template.engine import Engine
from django.template.exceptions import TemplateSyntaxError
from django.template.library import import_library
from django.utils.deconstruct import deconstructible


@deconstructible
class TemplateValidator(object):
    disallowed_tags = [
        'load',
        'extends',
        'include',
        'debug',
        'csrf_token',
    ]
    libraries = Engine.default_builtins + [
        'statistics.templatetags.statistics_tags',
    ]

    def _disallowed_tag(self, *args, **kwargs):
        raise TemplateSyntaxError('{} tags are not allowed'.format(', '.join(self.disallowed_tags)))

    def __call__(self, value):
        # Try to parse the template looking for syntax errors.
        lexer = Lexer(value)
        tokens = lexer.tokenize()
        parser = Parser(
            tokens,
            builtins=[import_library(path) for path in self.libraries],
        )

        for tag in self.disallowed_tags:
            parser.tags[tag] = self._disallowed_tag

        try:
            parser.parse()
        except TemplateSyntaxError as exc:
            raise ValidationError(str(exc))

    def __eq__(self, other):
        return isinstance(other, self.__class__)


validate_template = TemplateValidator()
