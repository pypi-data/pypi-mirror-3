import grok

from grokcore import message
from zope import component
from zope import security
from zope.site.hooks import getSite
from zope.interface import Interface

from horae.core.interfaces import IHorae, IAppConfiguration

from horae.layout import layout
from horae.layout.interfaces import IDisplayView, IBreadcrumbs

grok.templatedir('viewlet_templates')
grok.context(Interface)

# Viewletmanagers


class TopManager(grok.ViewletManager):
    """ Viewlet manager rendered on top
    """
    grok.name('top')


class HeaderLeftManager(grok.ViewletManager):
    """ Viewlet manager rendered on the left in the header
    """
    grok.name('header.left')


class HeaderRightManager(grok.ViewletManager):
    """ Viewlet manager rendered on the right in the header
    """
    grok.name('header.right')


class ContentBeforeManager(grok.ViewletManager):
    """ Viewlet manager rendered before the content
    """
    grok.name('content.before')


class ContentAfterManager(grok.ViewletManager):
    """ Viewlet manager rendered after the content
    """
    grok.name('content.after')


class SidebarManager(grok.ViewletManager):
    """ Viewlet manager rendered in the sidebar
    """
    grok.name('sidebar')


class FooterManager(grok.ViewletManager):
    """ Viewlet manager rendered in the footer
    """
    grok.name('footer')

# Viewlets


class Breadcrumbs(layout.Viewlet):
    """ Renders the breadcrumbs
    """
    grok.viewletmanager(HeaderRightManager)
    grok.order(20)

    def update(self):
        self.items = []
        adapter = component.queryMultiAdapter((self.view, self.request), interface=IBreadcrumbs)
        if adapter is not None:
            self.items.insert(0, adapter)
        item = self.context
        while not IHorae.providedBy(item):
            adapter = component.queryMultiAdapter((item, self.request), interface=IBreadcrumbs)
            if adapter is not None and security.checkPermission(adapter.permission, item):
                self.items.insert(0, adapter)
            item = item.__parent__


class Title(layout.Viewlet):
    """ Renders the title of the application
    """
    grok.viewletmanager(HeaderLeftManager)
    grok.order(10)

    def update(self):
        config = IAppConfiguration(getSite())
        self.title = config.title
        self.description = config.description


class MainNavigation(layout.Viewlet):
    """ Renders the main navigation
    """
    grok.viewletmanager(TopManager)
    grok.order(10)


class EditNavigation(layout.Viewlet):
    """ Renders the edit navigation
    """
    grok.viewletmanager(TopManager)
    grok.order(20)


class MainActionsMenu(layout.Viewlet):
    """ Renders the main actions menu
    """
    grok.viewletmanager(ContentBeforeManager)
    grok.order(0)
    grok.view(IDisplayView)


class Messages(layout.Viewlet):
    """ Renders the messages
    """
    grok.viewletmanager(HeaderRightManager)
    grok.order(100)

    def update(self):
        self.messages = [msg for msg in message.receive()]
