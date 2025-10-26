from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, arg):
    """
    Replace occurrences of arg[0] with arg[1] in value.
    Usage: {{ string|replace:"old,new" }}
    """
    if not arg or ',' not in arg:
        return value
    old, new = arg.split(',', 1)
    return value.replace(old, new)
