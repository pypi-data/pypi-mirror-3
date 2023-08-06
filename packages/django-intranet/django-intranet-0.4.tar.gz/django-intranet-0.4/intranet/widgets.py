# -*- coding: utf-8 -*-

import datetime
import re

import floppyforms as forms

from django.db import models
from django.utils.translation import ugettext as _

from south.modelsinspector import add_introspection_rules
from intranet.templatetags.intranet_values_extras import phone as phone_render, siret as siret_render


################
# Phone Widget
################
EMPTY_VALUES = (None, '')
    
class PhoneInput (forms.TextInput):
    def render(self, name, value, attrs=None):
        if value not in EMPTY_VALUES:
            value = phone_render(value)
        else:
            value = phone_render('')

        return super(PhoneInput, self).render(name, value, attrs)

class PhoneFormField(forms.CharField):
    widget = PhoneInput

    def clean(self, value):
        phone = super(PhoneFormField, self).clean(value)

        #print "PHONE =", phone
        
        # If the number is not empty, we process the entered data.
        if phone != "":
            # Does the number contain a telephone prefix?
            if phone.startswith('+'):
                mo = re.search(r'^\+\d{2,3}\.\d{9,11}$', phone)
                
                if not mo:
                    raise forms.ValidationError(_(u'You must enter a telephone number. (+33.389520638 or 0389520638).'))
                else:
                    return phone
          
            # No telephone prefix: we are in France by default
            phone = re.sub("\D", "", phone) # Removal of separating characters
        
            mo = re.search(r'^\d{10}$', phone) # 10-digit number
            if not mo:
                raise forms.ValidationError(_(u'You must enter a telephone number. (+33.389520638 ou 0389520638).'))
            else:
                phone = mo.group()[-9:]
            
            return u'+33.%s' % phone
        
        # The number is empty, we don't do anything.
        else:
            return phone

class PhoneField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 16
        super(PhoneField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def formfield(self, form_class=PhoneFormField, **kwargs):
        return super(PhoneField, self).formfield(form_class=form_class, **kwargs)

add_introspection_rules([], ["^intranet\.widgets\.PhoneField"])

###################
# SIRET code widget
###################
    
class SiretInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value not in EMPTY_VALUES:
            value = siret_render(value)
        else:
            value = phone_render('')

        return super(SiretInput, self).render(name, value, attrs)

class SiretFormField(forms.CharField):
    widget = SiretInput
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(SiretFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        
        if value in EMPTY_VALUES:
            return value
        else:
            siret = value.replace(' ','')
            if len(siret) != 14:
                raise forms.ValidationError(_(u'A SIRET number must contain exactly 14 digits.'))
            else:
                # Integer test
                try:
                    int(siret)
                except ValueError:
                    raise forms.ValidationError(_(u'A SIRET number must contain exactly 14 digits.'))
            
                # Validity test
                total = 0
                for i in range(14):
                    factor = (i % 2 == 0) and 2 or 1
                    itotal = factor * int(siret[i])
                    total += (itotal > 9) and itotal-9 or itotal
                    
                if total % 10 == 0:
                    return super(SiretFormField, self).clean(siret)
                else:
                    raise forms.ValidationError(_(u'The SIRET number you entered is invalid. Please enter a valid one.'))

class SiretField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 14
        super(SiretField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def formfield(self, form_class=SiretFormField, **kwargs):
        return super(SiretField, self).formfield(form_class=form_class, **kwargs)

add_introspection_rules([], ["^intranet\.widgets\.SiretField"])


# ------------------
# DatePicker Widget
# ------------------

class DatePicker(forms.TextInput):
    template_name = 'floppyforms/date.html'
    format="%d/%m/%Y"

    def render(self, name, value, attrs=None):
            if isinstance(value, datetime.date):
                    value=value.strftime(self.format)

            return super(DatePicker, self).render(name, value, attrs)
    
    # TODO: Dynamically load JS file instead of loading it in the template
    '''
    class Media:
        js = (
            '/_static/js/jquery-ui-timepicker-addon.js',
        )
    '''


# ------------------
# DateTimePicker Widget
# ------------------

class DateTimePicker(forms.TextInput):
    template_name = 'floppyforms/datetime.html'
    format="%d/%m/%Y %H:%M"

    def render(self, name, value, attrs=None):
            if isinstance(value, datetime.datetime):
                value=value.strftime(self.format)
            return super(DateTimePicker, self).render(name, value, attrs)
    
    # TODO: Dynamically load JS file instead of loading it in the template
    '''
    class Media:
        js = (
            '/_static/js/jquery-ui-timepicker-addon.js',
        )
    '''
