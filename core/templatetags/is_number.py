from django import template

register = template.Library()


@register.filter(is_safe=True)
def is_number(value):
    value = str(value)
    try:
        int(value)
        return True
    except ValueError:
        try:
            float(value)
            return True
        except ValueError:
            return False
