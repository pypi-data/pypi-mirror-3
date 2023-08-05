import grok
import os
import re

from BeautifulSoup import BeautifulSoup

from grokcore import message
from zope.site.hooks import getSite
from zope.component import getAdapters, getMultiAdapter, queryMultiAdapter, queryUtility
from zope.interface import Interface
from zope.i18n.interfaces import INegotiator

from horae.layout import _
from horae.layout import resource
from horae.layout import interfaces

grok.templatedir('templates')

LOCALES = None


def namespace(request):
    global LOCALES
    if LOCALES is None:
        LOCALES = [locale for locale in os.listdir(os.path.join(os.path.dirname(resource.__file__), 'locales')) if re.match('[a-z]{2}(-[A-Z]{2})?', locale)] + ['en']
    negotiator = queryUtility(INegotiator)
    return {'target_language': negotiator.getLanguage(LOCALES, request)}


class StyledViewMixin(object):
    """ Mix in class for views providing functionality to only render the
        content without the global template or even only a specified part
        specified by a CSS selector.

        Additionally this mix in class is responsible for including all the
        resources provided by the registered adapters implementing
        :py:class:`horae.layout.interfaces.IResourceProvider` and calling
        all adapters implementing :py:class:`horae.layout.interfaces.IViewExtender`.
    """

    def __call__(self, plain=False, selector=None):
        view = getMultiAdapter((self.context, self.request), name=u'global')
        self.plain = plain
        self.macro = plain and view.template.macros['plain'] or view.template.macros['layout']
        result = super(StyledViewMixin, self).__call__()
        if selector is None:
            return result
        soup = BeautifulSoup(result)
        return ''.join([node.renderContents() for node in soup.findSelect(selector)])

    def call_extenders(self, method, **params):
        for extender in self.extenders:
            getattr(extender, method)(**params)

    def namespace(self):
        return namespace(self.request)

    @property
    def actual_url(self):
        return self.url(self.context) + '/' + self.__name__

    @property
    def extenders(self):
        return [extender for name, extender in getAdapters((self,), interfaces.IViewExtender)]

    def update(self):
        self.call_extenders('pre_update')
        super(StyledViewMixin, self).update()
        self.call_extenders('post_update')
        self.resources()

    def resources(self):
        providers = getAdapters((self,), interfaces.IResourceProvider)
        for name, provider in providers:
            for resource in provider:
                resource.need()

    @property
    def base(self):
        return self.url(getSite())


class StyledFormMixin(StyledViewMixin):
    """ Mix in class for forms which calls the form specific methods
        of the registered adapters implementing
        :py:class:`horae.layout.interfaces.IViewExtender`.
    """

    def update(self):
        self.call_extenders('pre_update')
        super(StyledViewMixin, self).update()
        self.resources()

    def setUpWidgets(self, ignore_request=False):
        self.call_extenders('pre_setUpWidgets', ignore_request=ignore_request)
        super(StyledFormMixin, self).setUpWidgets(ignore_request)

    def update_form(self):
        super(StyledFormMixin, self).update_form()
        self.call_extenders('post_update')


class Global(grok.View):
    """ The global view used as template for all subclassing
        :py:class:`StyledViewMixin`
    """
    grok.context(Interface)
    grok.template('global')

    @property
    def base(self):
        return self.url(getSite())

    def namespace(self):
        return namespace(self.request)


class View(StyledViewMixin, grok.View):
    """ Basic view implementation meant to be subclassed by specific views
    """
    grok.baseclass()


class Form(StyledFormMixin, grok.Form):
    """ Basic form implementation meant to be subclassed by specific forms
    """
    grok.baseclass()
    grok.implements(interfaces.IEditView)
    grok.template('edit_form')
    id = ''
    cssClass = ''
    statusCssClass = ''

    def validate(self, action, data):
        errors = super(Form, self).validate(action, data)
        for extender in self.extenders:
            errors += extender.validate(action, data)
        return errors


class AddForm(StyledFormMixin, grok.AddForm):
    """ Basic add form implementation meant to be subclassed by specific add forms
    """
    grok.baseclass()
    grok.template('edit_form')
    grok.implements(interfaces.IAddForm)
    id = ''
    cssClass = ''
    statusCssClass = ''

    def validate(self, action, data):
        errors = super(AddForm, self).validate(action, data)
        for extender in self.extenders:
            errors += extender.validate(action, data)
        return errors

    @property
    def label(self):
        return _(u'Add ${type}', mapping={'type': self.object_type()})

    def object_type(self):
        return _(u'Item')

    def create(self, **data):
        raise NotImplementedError(u'concrete classes must implement create()')

    def add(self, obj):
        raise NotImplementedError(u'concrete classes must implement add()')

    def apply(self, obj, **data):
        self.applyData(obj, **data)
        self.call_extenders('apply', obj=obj, **data)

    def cancel(self):
        pass

    def next_url(self, obj):
        return self.url(obj)

    def cancel_url(self):
        return self.url(self.context)

    @property
    def msg(self):
        return _(u'${object} successfully added', mapping={'object': self.object_type()})

    @grok.action(_(u'Add'), name='add')
    def handle_add(self, **data):
        obj = self.create(**data)
        self.add(obj)
        self.apply(obj, **data)
        self.redirect(self.next_url(obj))
        message.send(self.msg, u'info', u'session')
        return ''

    @grok.action(_(u'Cancel'), name='cancel', validator=lambda *args, **kwargs: {})
    def handle_cancel(self, **data):
        self.cancel()
        self.redirect(self.cancel_url())
        return ''


class EditForm(StyledFormMixin, grok.EditForm):
    """ Basic edit form implementation meant to be subclassed by specific edit forms
    """
    grok.baseclass()
    grok.template('edit_form')
    grok.implements(interfaces.IEditForm)
    id = ''
    cssClass = ''
    statusCssClass = ''

    def validate(self, action, data):
        errors = super(EditForm, self).validate(action, data)
        for extender in self.extenders:
            errors += extender.validate(action, data)
        return errors

    @property
    def label(self):
        return _(u'Edit ${type}', mapping={'type': self.object_type()})

    def object_type(self):
        return _(u'Item')

    def apply(self, **data):
        self.applyData(self.context, **data)
        self.call_extenders('apply', obj=self.context, **data)

    def cancel(self):
        pass

    def next_url(self):
        return self.url(self.context)

    def cancel_url(self):
        return self.url(self.context)

    @property
    def msg(self):
        return _(u'Changes successfully saved')

    @grok.action(_(u'Save changes'), name='save')
    def handle_save(self, **data):
        self.apply(**data)
        self.redirect(self.next_url())
        message.send(self.msg, u'info', u'session')
        return ''

    @grok.action(_(u'Cancel'), name='cancel', validator=lambda *args, **kwargs: {})
    def handle_cancel(self, **data):
        self.cancel()
        self.redirect(self.cancel_url())
        return ''


class DisplayForm(StyledFormMixin, grok.DisplayForm):
    """ Basic display form implementation meant to be subclassed by specific display forms
    """
    grok.baseclass()
    grok.template('display_form')
    grok.implements(interfaces.IDisplayView)
    id = ''
    cssClass = ''


class DeleteForm(StyledFormMixin, grok.Form):
    """ Basic delete form implementation meant to be subclassed by specific delete forms
    """
    grok.baseclass()
    grok.template('delete_form')
    grok.implements(interfaces.IDeleteForm)
    id = ''
    cssClass = ''

    @property
    def label(self):
        return _(u'Delete ${type}', mapping={'type': self.object_type()})

    def object_type(self):
        return _(u'Item')

    def item_title(self):
        raise NotImplementedError(u'concrete classes must implement item_title()')

    def next_url(self):
        parent = self.context.__parent__
        while queryMultiAdapter((parent, self.request), name=u'index') is None:
            parent = parent.__parent__
        return self.url(parent)

    def cancel_url(self):
        return self.url(self.context)

    def delete(self):
        del self.context.__parent__[self.context.__name__]

    @property
    def msg(self):
        return _(u'${object} successfully deleted', mapping={'object': self.item_title()})

    @grok.action(_(u'Delete'), name='delete')
    def handle_delete(self, **data):
        self.redirect(self.next_url())
        msg = self.msg
        self.delete()
        message.send(msg, u'info', u'session')
        return ''

    @grok.action(_(u'Cancel'), name='cancel', validator=lambda *args, **kwargs: {})
    def handle_cancel(self, **data):
        self.redirect(self.cancel_url())
        return ''


class Viewlet(grok.Viewlet):
    """ Basic viewlet implementation meant to be subclassed by specific viewlets
    """
    grok.baseclass()

    def namespace(self):
        return namespace(self.request)


class BaseBreadcrumbs(grok.MultiAdapter):
    """ Adapter making an object visible in the breadcrumbs
    """
    grok.baseclass()
    grok.implements(interfaces.IBreadcrumbs)

    permission = 'horae.View'
    name = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def url(self):
        return grok.url(self.request, self.context)
