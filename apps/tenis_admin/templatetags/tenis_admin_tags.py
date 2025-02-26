# /tenismatch/apps/tenis_admin/templatetags/tenis_admin_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter para acessar valores de dicionário por chave
    Uso: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def replace(value, arg):
    """
    Template filter para substituir texto
    Uso: {{ value|replace:"_:" }} - substitui _ por espaço
    Uso: {{ value|replace:"_:!" }} - substitui _ por !
    """
    if value is None:
        return None
    
    try:
        old, new = arg.split(":")
        return value.replace(old, new)
    except ValueError:
        # Se não houver delimitador, substitui pelo espaço
        return value.replace(arg, " ")
