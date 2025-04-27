from django import template

register = template.Library()

@register.filter
def distinct_categories(consumables):
    seen = set()
    result = []
    for rek in consumables:
        if rek.catigories not in seen:
            seen.add(rek.catigories)
            result.append(rek)
    return result
