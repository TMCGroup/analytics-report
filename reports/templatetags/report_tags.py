from django import template

register = template.Library()


@register.filter('clean', needs_autoescape=True)
@register.simple_tag
def clean(groups_string):
    unclean_groups_list = groups_string[:-1].split(",")
    clean_groups_list = []
    for unclean_group in unclean_groups_list:
        clean_groups_list.append(unclean_group[3:-1])
    return clean_groups_list
