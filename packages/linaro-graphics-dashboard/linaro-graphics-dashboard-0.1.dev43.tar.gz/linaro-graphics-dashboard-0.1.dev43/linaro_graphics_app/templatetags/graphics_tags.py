from django import template

register = template.Library()

@register.filter
def key(d, key):
    return d.get(key, "")

@register.filter
def status_icon(status):
    status_attrs = {
        'pass': ('black', 'lawngreen','&#10003;'),
        'fail': ('black', 'red','&#10007;'),
        'unknown': ('black', 'lightgray', '?'),
        'increase': ('black', 'cornflowerblue','&#11014;'),
        'decrease': ('black', '#EE6464','&#11015;'),
        'superincrease': ('black', 'blue','&#11014;<span style="margin: 0 0.2em 0 -0.2em">!</span>')
        }

    attr = status_attrs.get(status, ('white', 'white', ''))
    span = '<span style="display: inline-block; width: 25px; height: 25px; border-radius: 25px; font-size: 150%%; color: %s; background-color: %s">%s</span>' % attr

    return span
