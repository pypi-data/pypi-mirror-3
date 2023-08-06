from django import forms
from django.conf import settings
from django.template.loader import render_to_string

class ColorPickerWidget(forms.TextInput):
    class Media:
        css = {
            'all': (settings.STATIC_URL + 'css/colorpicker.css',)
        }
        js = (settings.STATIC_URL + 'js/colorpicker.js',)

    def render(self, name, value, attrs=None):
        rendered = super(ColorPickerWidget, self).render(name, value, attrs)
        return rendered+ render_to_string('colorpicker.html', locals())
