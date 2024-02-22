from django import template

register = template.Library()

@register.filter(name='user_has_group')
def user_has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
