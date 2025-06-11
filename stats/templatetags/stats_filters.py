from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Фильтр для вычитания значений в шаблоне"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value