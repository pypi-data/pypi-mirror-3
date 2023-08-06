from __future__ import unicode_literals
from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe


class AceWidget(forms.Textarea):
    def __init__(self, mode=None, theme=None, *args, **kwargs):
        self.mode = mode
        self.theme = theme
        super(AceWidget, self).__init__(*args, **kwargs)

    @property
    def media(self):
        css = {'all': ['django_ace/widget.css']}
        js = [
            "django_ace/ace/ace.js",
            "django_ace/widget.js",
        ]
        if self.mode:
            js.append("django_ace/ace/mode-%s.js" % self.mode)
        if self.theme:
            js.append("django_ace/ace/theme-%s.js" % self.theme)
        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs=None):
        attrs = attrs or {}

        div_attrs = {
            "class": "django-ace-widget",
            "style": "display: none",
        }
        if self.mode:
            div_attrs["data-mode"] = self.mode
        if self.theme:
            div_attrs["data-theme"] = self.theme

        ace = '<div%s></div>' % flatatt(div_attrs)
        textarea = super(AceWidget, self).render(name, value, attrs)
        return mark_safe(ace + textarea)
