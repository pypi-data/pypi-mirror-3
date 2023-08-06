from django import template

register = template.Library()

import re

@register.filter(name='phone')
def phone(value):
    """
    Transform a number "+81.0123456789" into "+810123456789" and a number "+33.384289468" into "03 84 28 94 68" for better readablility.
    """

    if value.startswith('+33.'):
        # get 9 or 10 digits, or None:
        mo = re.search(r'\d{9,10}', value)

        # If the number is not standardized, we don't modify it.
        if mo is None: return value
        
        # add a leading 0 if they were just 9
        digits = mo.group().zfill(10)
        
        # now put a dot after each 2 digits
        return " ".join(re.findall(r'(\d\d)',digits))
    else:
        return re.sub(r'\+(\d{2,3})\.(\d{9,11})', r"+\1\2", value)

@register.filter(name='siret')
def siret(value):
    """
    Transform a SIRET code "73282932000074" into "732 829 320 00074" for better readability.
    """
    
    if value=='' :
        return ''
    else:
        return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{5})', r'\1 \2 \3 \4', value)

