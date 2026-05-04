from django import template

register = template.Library()

@register.filter
def precio_clp(value):
    try:
        valor = int(value)
        return f"{valor:,}".replace(",", ".")
    except:
        return value