# /tenismatch/apps/tenis_admin/templatetags/tenis_admin_tags.py
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def replace(value, arg):
    """
    Substitui uma string por outra no valor.
    Uso: {{ value|replace:"original:new" }}
    """
    if len(arg.split(':')) != 2:
        return value
    
    original, new = arg.split(':')
    return value.replace(original, new)

@register.filter
def get_item(dictionary, key):
    """
    Obtém um item de um dicionário pelo nome da chave.
    Uso: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def percentage(value):
    """
    Formata um valor como percentual.
    Uso: {{ value|percentage }}
    """
    if value is None:
        return "0%"
    return f"{float(value):.1f}%"