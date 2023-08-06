from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms import widgets
from django.forms.util import flatatt
from django.utils.html import escape
from django.utils.safestring import mark_safe

JS = (
	'rays/rays.js',
)
CSS = {
    'all': (
			'rays/rays.css',
        )
    }


class Input(widgets.Input):
    '''
    Subclasses django's base input widget and provides some helpers to inject
    custom css class names.
    '''
    input_type = 'text'


class AutocompleteInput(Input):
    class Media:
        js = JS
        css = CSS

    def __init__(self, urlname=None, url=None, attrs=None):
        assert url or urlname, u"Expects either 'url' or 'urlname'"
        self.urlname = urlname
        self.url = url
        super(AutocompleteInput, self).__init__(attrs)

    def build_attrs(self, extra_attrs, **kwargs):
        extra_attrs = extra_attrs or {}
        if self.urlname:
            url = reverse(self.urlname)
        else:
            url = self.url
        extra_attrs['data-rays-autocomplete-url'] = url
        return super(AutocompleteInput, self).build_attrs(extra_attrs, **kwargs)


class AutocompleteChoices(Input):
    class Media:
        js = JS
        css = CSS

    def __init__(self, choices, attrs=None):
        self.choices = choices
        super(AutocompleteChoices, self).__init__(attrs)

    def build_attrs(self, extra_attrs, extra_classes=None, **kwargs):
        attrs = super(AutocompleteChoices, self).build_attrs(extra_attrs, **kwargs)
        attrs['data-rays-autocomplete-choices'] = '%s_choices' % attrs['id']
        return attrs

    def render(self, name, value, attrs=None):
        html = [super(AutocompleteChoices, self).render(name, value, attrs)]
        choices_attrs = {'style': 'display:none;'}
        if 'id' in attrs:
            choices_attrs['id'] = '%s_choices' % attrs['id']
        html.append('<dl%s>' % flatatt(choices_attrs))
        for key, value in self.choices:
            html.append('<dt>%s</dt><dd>%s</dd>' % (escape(key), escape(value)))
        html.append('</dl>')
        return mark_safe(u''.join(html))


class DateInput(Input):
    input_type = 'date'
    format = 'yy-mm-dd'

    class Media:
        js = JS
        css = CSS

    def __init__(self, attrs=None, format=None):
        if format:
            self.format = format
        super(DateInput, self).__init__(attrs)

    def build_attrs(self, extra_attrs, **kwargs):
        extra_attrs = extra_attrs or {}
        extra_attrs['data-rays-datepicker-format'] = self.format
        return super(DateInput, self).build_attrs(extra_attrs, **kwargs)


class RangeInput(Input):
    '''
    Displays a ``<div>`` after the input tag which is used to render the
    jquery ui slider. The ``div`` gets the ``rays-slider-ui`` css class and
    the same id as the ``input`` appended with ``_slider``.
    '''
    input_type = 'range'

    class Media:
        js = JS
        css = CSS

    def __init__(self, attrs=None, min_value=0, max_value=100, step=None):
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        super(RangeInput, self).__init__(attrs)

    def build_attrs(self, extra_attrs, **kwargs):
        extra_attrs = extra_attrs or {}
        extra_attrs['min'] = self.min_value
        extra_attrs['max'] = self.max_value
        if self.step is not None:
            extra_attrs['step'] = self.step
        return super(RangeInput, self).build_attrs(extra_attrs, **kwargs)



class ValidationInput(Input):
    class Media:
        js = JS
        css = CSS

    def __init__(self, urlname=None, url=None, attrs=None, widget=None):
        assert url or urlname, u"Expects either 'url' or 'urlname'"
        self.urlname = urlname
        self.url = url
        self.widget = widget or widgets.TextInput(attrs)
        super(ValidationInput, self).__init__(None)

    def build_attrs(self, extra_attrs, extra_classes=None, **kwargs):
        extra_classes = extra_classes or []
        if self.urlname:
            url = reverse(self.urlname)
        else:
            url = self.url
        extra_classes.append('rays-validation')
        extra_classes.append(':validate;url;%s' % url)
        return super(ValidationInput, self).build_attrs(
            extra_attrs, extra_classes=extra_classes, **kwargs)

    def render(self, name, value, attrs=None):
        attrs = self.build_attrs({})
        return self.widget.render(name, value, attrs)
