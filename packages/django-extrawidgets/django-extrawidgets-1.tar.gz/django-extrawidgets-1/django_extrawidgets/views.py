from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.utils import simplejson


def autocomplete(request, queryset, field_name, label=None, limit=None,
    casesensitive=False):
    '''
    Generic autocompletion view used with `jQuery UI Autocomplete`_.

    You need to pass a ``queryset`` instance which provides the actual output
    that should be suggested as completion. The ``field_name`` parameter
    specifies the model field which is used to search in the queryset. Define
    the maximum returned results with ``limit``.

    The jQuery widget supports a separation between the value that is entered
    into the input field and the label that is displayed in the selection list
    while autocompleting. If you want to display something different in this
    list, provide a callable as ``label`` parameter which accepts a model
    instance as argument and returns the text that will be used as label.

    Set ``casesensitive`` to ``True`` if you only want to get items that also
    matches in case. This type of lookup does not work for sqlite databases.

    The view returns a list of autocomplete suggestions with each suggestion
    in a single line.

    .. _jQuery UI Autocomplete: http://docs.jquery.com/UI/Autocomplete
    '''
    if 'term' not in request.GET:
        raise Http404(u"specify a 'term' GET parameter")
    if casesensitive:
        lookup_style = 'startswith'
    else:
        lookup_style = 'istartswith'
    lookup = {'%s__%s' % (field_name, lookup_style): request.GET['term']}
    queryset = queryset.filter(**lookup)
    if label is None:
        if limit:
            queryset = queryset[:limit]
        values = list(queryset.values_list(field_name, flat=True))
    else:
        if limit:
            queryset = queryset[:limit]
        values = []
        for obj in queryset:
            values.append({
                'value': getattr(obj, field_name),
                'label': label(obj),
            })
    return HttpResponse(
        simplejson.dumps(values),
        mimetype='application/json')


def validate_form(request, form_class, prefix=None):
    '''
    Helper for ajax-based server side form validation with `jQuery Validation
    Plugin`_

    .. _jQuery Validation Plugin: http://docs.jquery.com/Plugins/Validation
    '''
    form = form_class(request.GET, prefix=prefix)
    errors = form.errors
    return HttpResponse(
        simplejson.dumps(errors),
        mimetype=u'application/json')


def validate(request, validator=None, form_class=None, field_name=None):
    '''

    '''
    assert validator or form_class and field_name, \
        u"Specify 'validator' or 'field' and 'form'"
    if 'value' not in request.GET:
        raise Http404(u"specify a 'value' GET parameter")
    value = request.GET['value']
    errors = []
    try:
        if validator:
            validator(value)
    except ValidationError, e:
        errors.extend(e.messages)
    if form_class and field_name:
        form = form_class({field_name: value})
        errors.extend(form[field_name].errors)
    return HttpResponse(
        simplejson.dumps(errors),
        mimetype='application/json')
