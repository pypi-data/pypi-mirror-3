import grok

from zope import interface
from zope import component
from zope.i18n import translate
from zope.i18nmessageid.message import Message

from megrok import navigation
from grokcore import message

from horae.core.interfaces import IHorae, IAppConfigurationHolder, IAppConfiguration, IApplicationUpgrader, IWorkdays, ISizeFormatter

from horae.layout import _
from horae.layout import layout
from horae.layout import interfaces

grok.templatedir('templates')


class Index(layout.View):
    """ Default view of horae
    """
    grok.context(IHorae)
    grok.implements(interfaces.IDisplayView, interfaces.IViewView)
    grok.require('zope.View')
    navigation.sitemenuitem(interfaces.IMainNavigation, _(u'Home'), order=0)


class AppConfiguration(layout.EditForm):
    """ Form to edit the application configuration specified by
        :py:class:`horae.core.interfaces.IAppConfiguration`
    """
    grok.context(IAppConfigurationHolder)
    grok.require('horae.Manage')
    grok.name('configure-app')
    navigation.sitemenuitem(interfaces.IGlobalManageMenu, _(u'Application configuration'), order=1)

    label = _(u'Application configuration')
    form_fields = grok.AutoFields(IAppConfiguration)

    def apply(self, **data):
        super(AppConfiguration, self).apply(**data)
        component.getUtility(IWorkdays).invalidate()


class Upgrade(layout.View):
    """ View to upgrade the application
    """
    grok.context(IHorae)
    grok.name('upgrade')
    grok.require('horae.Manage')
    navigation.sitemenuitem(interfaces.IGlobalManageMenu, _(u'Upgrade application'), order=20)

    def results(self):
        return '\n'.join(IApplicationUpgrader(self.context).upgrade())


class Pack(layout.View):
    """ View to pack the database
    """
    grok.context(IHorae)
    grok.require('horae.Manage')
    navigation.sitemenuitem(interfaces.IGlobalManageMenu, _(u'Pack database'), order=100)

    def __call__(self):
        before = self.request.publication.db.getSize()
        self.request.publication.db.pack()
        after = self.request.publication.db.getSize()
        formatter = ISizeFormatter(self.request)
        self.redirect(self.request.get('HTTP_REFERER', self.url(self.context)))
        message.send(_(u'Database successfully packed. The database size was reduced from ${before} to ${after}', mapping={'before': formatter.format(before),
                                                                                                                           'after': formatter.format(after)}), u'info', u'session')

    def render(self):
        return ''


class Translate(layout.View):
    """ View to translate a given string
    """
    grok.context(interface.Interface)
    grok.require('zope.View')

    def render(self, msgid, domain=None, default=None, mapping=None):
        return translate(Message(msgid, domain, default, mapping), context=self.request)
