import datetime

from zope.formlib.i18n import _ as _z
from zope.formlib import textwidgets
from zope.formlib import widget
from zope.datetime import DateTimeError
from zope.formlib.interfaces import ConversionError

from fanstatic import Resource

from horae.datetime import resource


class DateWidgetMixin(object):
    """ Mix in class for date widgets adding the needed js and css resources
    """

    def __call__(self):
        uii18n = resource.jqueryui_i18n(self.request)
        if uii18n is not None:
            js = Resource(resource.library, 'datetime.js', [uii18n, resource.spinbox])
        else:
            js = resource.js
        js.need()
        resource.css.need()
        return u''


class DateWidget(DateWidgetMixin, textwidgets.DateI18nWidget):
    """ Date widget displaying a localized calendar to select the date
    """
    displayStyle = 'short'

    def __call__(self):
        super(DateWidget, self).__call__()

        value = self._getFormValue()
        if value is None or value == self.context.missing_value:
            value = ''

        kwargs = {'type': self.type,
                  'name': self.name,
                  'id': self.name,
                  'value': value,
                  'cssClass': self.cssClass + ' date',
                  'style': self.style,
                  'size': self.displayWidth,
                  'data-format': self.request.locale.dates.getFormatter('date', 'short').getPattern().lower(),
                  'extra': self.extra}
        if self.displayMaxWidth:
            kwargs['maxlength'] = self.displayMaxWidth # TODO This is untested.

        return widget.renderElement(self.tag, **kwargs)


class DatetimeWidget(DateWidgetMixin, textwidgets.DatetimeI18nWidget):
    """ Date/time widget displaying a localized calendar to select the date and
        an hour and minute field to define the time
    """
    displayStyle = 'short'
    _category = 'date'

    def __call__(self):
        super(DatetimeWidget, self).__call__()

        value = self._getFormValue()
        if value is None or value == self.context.missing_value:
            value = {}

        kwargs = {'type': self.type,
                  'name': self.name,
                  'id': self.name,
                  'value': value.get('date', ''),
                  'cssClass': self.cssClass + ' date',
                  'style': self.style,
                  'size': self.displayWidth,
                  'extra': self.extra}
        if self.displayMaxWidth:
            kwargs['maxlength'] = self.displayMaxWidth # TODO This is untested.

        date_kwargs = kwargs.copy()
        date_kwargs.update({'name': self.name + '.date:record',
                            'size': self.displayWidth - 5,
                            'value': value.get('date', ''),
                            'data-format': self.request.locale.dates.getFormatter('date', 'short').getPattern().lower(),
                            'cssClass': self.cssClass + ' date'})

        hours_kwargs = kwargs.copy()
        hours_kwargs.update({'name': self.name + '.hours:record',
                             'value': value.get('hours', ''),
                             'cssClass': self.cssClass + ' hours spinbox',
                             'size': 2,
                             'maxlength': 2})

        minutes_kwargs = kwargs.copy()
        minutes_kwargs.update({'name': self.name + '.minutes:record',
                               'value': value.get('minutes', ''),
                               'cssClass': self.cssClass + ' minutes spinbox',
                               'size': 2,
                               'maxlength': 2})

        return widget.renderElement(self.tag, **date_kwargs) + \
               widget.renderElement(self.tag, **hours_kwargs) + \
               widget.renderElement(self.tag, **minutes_kwargs)

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        else:
            try:
                input = dict(input)
                if not input['hours']:
                    input['hours'] = 0
                input['hours'] = min(23, max(0, int(input['hours'])))
                if not input['minutes']:
                    input['minutes'] = 0
                input['minutes'] = min(59, max(0, int(input['minutes'])))
                date = super(DatetimeWidget, self)._toFieldValue(input['date'])
                if date is None:
                    return None
                return datetime.datetime(date.year, date.month, date.day, hour=input['hours'], minute=input['minutes'])
            except (DateTimeError, ValueError, IndexError), v:
                raise ConversionError(_z("Invalid datetime data"), v)

    def _toFormValue(self, value):
        value = super(textwidgets.TextWidget, self)._toFormValue(value)
        if value:
            formatter = self.request.locale.dates.getFormatter(
                'date', (self.displayStyle or None))
            value = {'date': formatter.format(value),
                     'hours': value.time().hour,
                     'minutes': value.time().minute}
        else:
            value = {}
        return value
