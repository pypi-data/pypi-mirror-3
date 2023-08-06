from datetime import datetime
from yafowil.base import (
    factory,
    UNSET,
    ExtractionError,
    fetch_value
)
from yafowil.common import (
    generic_extractor,
    generic_required_extractor,
)
from yafowil.utils import (
    cssid,
    cssclasses,
    css_managed_props,
    managedprops,
)
from bda.intellidatetime import (
    convert,
    LocalePattern,
    DateTimeConversionError,
)

def call_if_callable(key, widget, data):
    attr = widget.attrs[key]
    if callable(attr):
        return attr(widget, data)
    return attr

def datetime_extractor(widget, data):
    time = None
    if call_if_callable('time', widget, data):
        time = data.request.get('%s.time' % widget.dottedpath)
    if not widget.attrs['required'] and not data.extracted and not time:
        return ''
    locale = call_if_callable('locale', widget, data)
    tzinfo = call_if_callable('tzinfo', widget, data)
    try:
        return convert(data.extracted, time=time, tzinfo=tzinfo, locale=locale)
    except DateTimeConversionError:
        raise ExtractionError('Not a valid date input.')


_mapping = {
    'D': 'day',
    'M': 'month',
    'Y': 'year',
}

def format_date(dt, locale, delim):
    pattern = LocalePattern().date(locale)
    ret = ''
    for char in pattern.split(' '):
        ret = '%s%s%s' % (ret, delim, getattr(dt, _mapping[char]))
    return ret.strip(delim)


def format_time(dt):
    return '%02i:%02i' % (dt.hour, dt.minute)


def render_datetime_input(widget, data, date, time):
    tag = data.tag
    timeinput = ''
    if time:
        if time is True:
            time = ''
        if not time and data.request:
            time = data.request.get('%s.time' % widget.dottedpath)
        timeinput = tag('input', **{
            'type': 'text',
            'value': time,
            'name_': '%s.time' % widget.dottedpath,
            'id': cssid(widget, 'input', 'time'),
            'size': 5,
        })
    additional_classes = []
    if widget.attrs['datepicker']:
        additional_classes.append(widget.attrs['datepicker_class'])
    attrs = {
        'type': 'text',
        'value':  date,
        'name_': widget.dottedpath,
        'id': cssid(widget, 'input'),
        'class_': cssclasses(widget, data, additional=additional_classes),
        'size': 10,
    }
    return tag('input', **attrs) + timeinput


@managedprops('locale', *css_managed_props)
def datetime_edit_renderer(widget, data):
    locale = call_if_callable('locale', widget, data)
    delim = call_if_callable('delimiter', widget, data)
    time = call_if_callable('time', widget, data)
    date = None
    if data.value and isinstance(data.value, datetime):
        date = format_date(data.value, locale, delim)
        if time:
            time = format_time(data.value)
    if data.extracted and isinstance(data.extracted, datetime):
        date = format_date(data.extracted, locale, delim)
        if time:
            time = format_time(data.extracted)
    if not date:
        date = fetch_value(widget, data)
    return render_datetime_input(widget, data, date, time)


def datetime_display_renderer(widget, data):
    if not data.value:
        return u''
    format = widget.attrs['format']
    if callable(format):
        value = format(widget, data)
    else:
        value = data.value.strftime(format)
    attrs = {
        'id': cssid(widget, 'display'),
        'class_': 'display-%s' % widget.attrs['class']
    }
    return data.tag('div', value, **attrs)


factory.register(
    'datetime',
    extractors=[generic_extractor, generic_required_extractor,
                datetime_extractor],
    edit_renderers=[datetime_edit_renderer],
    display_renderers=[datetime_display_renderer])

factory.doc['blueprint']['datetime'] = \
"""Add-on blueprint `yafowil.widget.datetime 
<http://github.com/bluedynamics/yafowil.widget.datetime/>`_ .
"""

factory.defaults['datetime.default'] = ''

factory.defaults['datetime.class'] = 'datetime'

factory.defaults['datetime.required_class'] = 'required'

factory.defaults['datetime.datepicker_class'] = 'datepicker'

factory.defaults['datetime.datepicker'] = False
factory.doc['props']['datetime.datepicker'] = \
"""Flag whether datepicker should be rendered.
"""

factory.defaults['datetime.time'] = False
factory.doc['props']['datetime.time'] = \
"""Flag whether time input should be rendered.

``time`` may be a callable taking widget and data as parameters expect to return 
a boolean.
"""

factory.defaults['datetime.tzinfo'] = None
factory.doc['props']['datetime.tzinfo'] = \
"""Python datetime tzinfo object.

``tzinfo`` may be a callable taking widget and data as parameters expect to 
return a tzinfo instance.
"""

factory.defaults['datetime.locale'] = 'iso'
factory.doc['props']['datetime.locale'] = \
"""Date input format locale. ``yafowil.widget.datetime`` uses
`bda.intellidatetime <http://pypi.python.org/pypi/bda.intellidatetime/>`_ for
input parsing. Take a look at this package for available locales.

``locale`` may be a callable taking widget and data as parameters expect to 
return a locale string.
"""

factory.defaults['datetime.delimiter'] = '-'
factory.doc['props']['datetime.delimiter'] = \
"""Delimiter used to render date in input field.

``delimiter`` may be a callable taking widget and data as parameters expect to 
return a delimiter string.
"""

factory.defaults['datetime.format'] = '%Y-%m-%d %H:%M'
factory.doc['props']['datetime.format'] = \
"""Pattern accepted by ``datetime.strftime`` or callable taking widget and 
data as parameters returning unicode or utf-8 string. Used if widget mode is 
``display``.
"""
