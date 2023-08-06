import django.core.validators
from django import forms
from django.template.defaultfilters import escapejs
from django.utils.encoding import force_unicode, StrAndUnicode


__all__ = ('format_error_message', 'js_validator', 'JavascriptValidation')


JS_VALIDATORS = {}


def format_error_message(message):
    return escapejs(force_unicode(message));


def js_validator(validator):
    def decorator(func):
        JS_VALIDATORS[validator] = func
        return func
    return decorator


@js_validator(forms.IntegerField)
def validate_integer(field):
    return '''function (value) {
        if (isNaN(parseInt(value))) {
            return "%s";
        }
    }''' % format_error_message(field.error_messages['invalid'])


class JS_BaseValidator(object):
    def __init__(self, compare, show_value='value'):
        self.compare = compare
        self.show_value = show_value

    def get_message(self, validator, field):
        try:
            message = field.error_messages[validator.code]
        except KeyError:
            message = validator.message
        return format_error_message(message)

    def __call__(self, validator, field):
        values = {
            'limit_value': validator.limit_value,
            'message': self.get_message(validator, field),
        }
        values['compare'] = self.compare % values
        values['show_value'] = self.show_value
        return '''function (value) {
            if (%(compare)s) {
                return interpolate("%(message)s", {
                    limit_value: %(limit_value)d,
                    show_value: %(show_value)s
                });
            }
        }''' % values


min_value_validator = JS_BaseValidator('parseInt(value) < %(limit_value)d')
max_value_validator = JS_BaseValidator('parseInt(value) > %(limit_value)d')
min_length_validator = JS_BaseValidator(
    'value.length < %(limit_value)d',
    'value.length')
max_length_validator = JS_BaseValidator(
    'value.length > %(limit_value)d',
    'value.length')

js_validator(django.core.validators.MinValueValidator)(min_value_validator)
js_validator(django.core.validators.MaxValueValidator)(max_value_validator)
js_validator(django.core.validators.MinLengthValidator)(min_length_validator)
js_validator(django.core.validators.MaxLengthValidator)(max_length_validator)


class JavascriptValidation(StrAndUnicode):
    def __init__(self, form):
        self.form = form

    def required_validator(self, field):
        message = field.error_messages[u'required']
        return u'''{
            validate: function (value) {
                if (!value && value !== 0) {
                    return "%s";
                }
            },
            stopOnError: true
        }''' % escapejs(message)

    def get_fields(self):
        # get list of bounded fields
        return list(self.form)

    def get_js_validators_for_field(self, bound_field):
        field = bound_field.field
        validators = []
        # "required" validation logic is not in a validator so we need a
        # custom solution
        if field.required:
            validators.append(self.required_validator(field))
        if field.__class__ in JS_VALIDATORS:
            js_validator = JS_VALIDATORS[field.__class__]
            validators.append(js_validator(field))
        for validator in field.validators:
            js_validator = self.get_js_for_validator(validator, field)
            validators.append(js_validator)
        return validators

    def get_js_for_field(self, bound_field):
        validators = self.get_js_validators_for_field(bound_field)
        html = []
        for validator in validators:
            if validator:
                html.append(u'''$('#%s').addValidator(%s);''' % (
                    bound_field.auto_id, validator))
        return u'\n'.join(html)

    def get_js_for_validator(self, validator, field):
        '''
        Get a javascript validator from a python validator. It checks the
        ``js_validator`` attribute of the python validator first to get a
        string or a callable that returns a string which is a javascript
        validator.
        Otherwise use the JS_VALIDATORS registery to lookup a javascript
        validator.
        '''
        if hasattr(validator, 'js_validator'):
            if callable(validator.js_validator):
                return validator.js_validator()
            return validator.js_validator
        if validator in JS_VALIDATORS:
            js_validator = JS_VALIDATORS[validator]
            return js_validator(validator, field)
        if validator.__class__ in JS_VALIDATORS:
            js_validator = JS_VALIDATORS[validator.__class__]
            return js_validator(validator, field)
        # TODO: maybe introduce a way to support subclassed validator classes
        return None

    def __unicode__(self):
        html = []
        for field in self.get_fields():
            validator = self.get_js_for_field(field)
            if validator:
                html.append(validator)
        return u'\n'.join(html)
