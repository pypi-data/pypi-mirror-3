from DateTime import DateTime
from Products.ATContentTypes.utils import dt2DT
from Products.ATContentTypes.utils import DT2dt
from zope.app.form.browser.textwidgets import DatetimeWidget
from zope.app.form.interfaces import WidgetInputError
from zope.app.pagetemplate import ViewPageTemplateFile


class dtwidget(DatetimeWidget):

    __call__ = ViewPageTemplateFile('dtwidget.pt')

    tag = u'input'
    cssClass = u''
    extra = u''
    _missing = u''

    def getDT(self):
        try:
            value = self._getFormValue()
            if not value:
                return self._missing
        except AttributeError:
            return self._missing
        return dt2DT(value)

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        else:
            try:
                DT = DateTime(input)
            except Exception:
                raise WidgetInputError("Invalid date", input)
            return DT2dt(DT)
