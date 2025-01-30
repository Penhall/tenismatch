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