from django import template

register = template.Library()


@register.filter('clean', needs_autoescape=True)
@register.simple_tag
def clean(ls):
    ls = "".join(ls)
    nls = ls[:-1].split(",")
    groups = []
    for st in nls:
        groups.append(st[3:-1])
    return groups
