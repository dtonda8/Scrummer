from django import template

register = template.Library()

@register.filter(name='get_property')
def get_property(dict, key):
    if dict is None:
        return None
    return dict.get(key)
    