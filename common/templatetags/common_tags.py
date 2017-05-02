from django import template


register = template.Library()


@register.filter
def first_block_of(blocks, type):
    for block in blocks:
        if block.block_type == type:
            return block
