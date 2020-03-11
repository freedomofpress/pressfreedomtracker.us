import html

from django.core.exceptions import ValidationError
from django.template.base import Parser, Lexer, Node, TokenType
from django.template.engine import Engine
from django.template.exceptions import TemplateSyntaxError
from django.template.library import import_library
from django.utils.deconstruct import deconstructible

from common.models import CustomImage


def tag_validator(library, tag_name):
    def dec(func):
        tag = library.tags[tag_name]

        # Wrap the validate function so that authors don't
        # have to return a fake node.
        def validate(parser, token):
            func(parser, token)
            return Node()

        tag._validate = validate
        return func
    return dec


def validate_image_format(value):
    try:
        logo_image = CustomImage.objects.get(pk=value)
    except CustomImage.DoesNotExist:
        pass
    else:
        logo_image_filename = logo_image.file.name.lower().strip()
        if logo_image_filename.endswith('jpg') or logo_image_filename.endswith('jpeg'):
            raise ValidationError(
                'Please upload a non JPEG format image for footer logos',
            )


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
        for token in tokens:
            if token.token_type == TokenType.BLOCK:
                token.contents = html.unescape(token.contents)
        parser = Parser(
            tokens,
            builtins=[import_library(path) for path in self.libraries],
        )

        for tag in self.disallowed_tags:
            parser.tags[tag] = self._disallowed_tag

        # Allow tags to define a substitue function to validate the tag
        # more precisely than we normally would (because statistics tags
        # should only raise template syntax errors for syntax errors,
        # not incorrect params - but here we want to catch both.)
        for tag, compile_func in parser.tags.items():
            if hasattr(compile_func, '_validate'):
                parser.tags[tag] = compile_func._validate

        try:
            parser.parse()
        except TemplateSyntaxError as exc:
            raise ValidationError(str(exc))

    def __eq__(self, other):
        return isinstance(other, self.__class__)


validate_template = TemplateValidator()
