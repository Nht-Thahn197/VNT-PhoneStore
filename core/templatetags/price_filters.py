from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template

register = template.Library()


@register.filter(name="format_vnd")
def format_vnd(value):
    if value is None:
        return ""
    try:
        amount = Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return value

    formatted = f"{int(amount):,}".replace(",", ".")
    return f"{formatted}đ"
