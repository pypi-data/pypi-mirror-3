from zope import component
from zope import formlib
from zope.i18n import translate
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.formlib.interfaces import IWidgetInputErrorView
from zope.formlib.itemswidgets import \
    DropdownWidget as BaseDropdownWidget, \
    MultiCheckBoxWidget as BaseMultiCheckBoxWidget
from zope.formlib.sequencewidget import \
    ListSequenceWidget as BaseListSequenceWidget, \
    SequenceDisplayWidget as BaseSequenceDisplayWidget
from zope.formlib.objectwidget import ObjectWidget as BaseObjectWidget
from zope.browserpage import ViewPageTemplateFile
from fanstatic import core
from z3c.widget.tiny.widget import TinyWidget

from horae.core import utils

from horae.layout import _
from horae.layout import resource


class ListSequenceWidget(BaseListSequenceWidget):
    template = ViewPageTemplateFile('templates/sequencewidget.pt')

    def addButtonLabel(self):
        return _('Add ${type}', mapping={'type': self.context.title or self.context.__name__})


class SequenceDisplayWidget(BaseSequenceDisplayWidget):
    tag = "ul"


class MultiCheckBoxWidget(BaseMultiCheckBoxWidget):
    cssClass = 'MultiCheckBoxWidget'


class DropdownWidget(BaseDropdownWidget):

    _messageNoValue = _(u'(nothing selected)')

    def renderItemsWithValues(self, values):
        missing = self._toFormValue(self.context.missing_value)
        if missing in values and self.context.default is not None:
            values = [self.context.default, ]
        return super(DropdownWidget, self).renderItemsWithValues(values)


class ObjectWidget(BaseObjectWidget):
    def error(self):
        if self._error:
            errormessages = []
            keys = self._error.keys()
            keys.sort()
            for key in keys:
                error = component.getMultiAdapter((self._error[key], self.request), IWidgetInputErrorView).snippet()
                if not error:
                    continue
                errormessages.append('%s: %s' % (translate(self._error[key].widget_title, context=self.request, default=self._error[key].widget_title),
                                                 error))
            if not len(errormessages):
                return ""
            return '<div class="form-status"><ul class="errors"><li>' + '</li><li>'.join(errormessages) + '</li></ul></div>'
        return ""


class DateDisplayWidget(formlib.textwidgets.DateDisplayWidget):
    displayStyle = 'short'

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        if content == self.context.missing_value:
            return ""
        return utils.formatDateTime(content, self.request, (self._category, self.displayStyle))


class DatetimeDisplayWidget(formlib.textwidgets.DatetimeDisplayWidget):
    displayStyle = 'short'

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        if content == self.context.missing_value:
            return ""
        category = self._category
        if content.hour == 0 or content.minute == 0:
            self._category = 'date'
        result = utils.formatDateTime(content, self.request, (self._category, self.displayStyle))
        self._category = category
        return result


class SimpleTinyWidget(TinyWidget):

    def __call__(self, *args, **kw):
        content_css = []
        needed = core.NeededResources()
        needed.base_url = absoluteURL(None, self.request)
        needed.need(resource.editor)
        for r in needed.resources():
            content_css.append('%s/%s' % (needed.library_url(resource.library), r.relpath))
        self.mce_content_css = ','.join(content_css)
        self.mce_plugins = ''
        self.mce_theme_advanced_buttons1 = 'bold,italic,underline,separator,bullist,numlist,indent,outdent,separator,link,unlink,separator,sub,sup,separator,formatselect'
        self.mce_theme_advanced_buttons2 = ''
        self.mce_theme_advanced_buttons3 = ''
        self.mce_theme_advanced_blockformats = 'p,pre,h4,h5,h6'
        self.mce_theme_advanced_toolbar_location = 'top'
        self.mce_theme_advanced_toolbar_align = 'left'
        self.mce_theme_advanced_statusbar_location = 'bottom'
        return super(SimpleTinyWidget, self).__call__(*args, **kw)


class DecimalI18NDisplayWidget(formlib.widget.UnicodeDisplayWidget):

    def __call__(self):
        value = super(DecimalI18NDisplayWidget, self).__call__()
        if not value:
            return value
        formatter = self.request.locale.numbers.getFormatter('decimal')
        return formatter.format(float(value))
