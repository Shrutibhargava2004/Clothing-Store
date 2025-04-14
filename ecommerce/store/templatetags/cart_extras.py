
from django import template

register = template.Library()

@register.simple_tag
def to_range(start, end):
    return range(int(start), int(end))
