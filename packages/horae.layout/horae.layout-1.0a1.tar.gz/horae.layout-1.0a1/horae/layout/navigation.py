import grok

from zope import component
from zope.viewlet.interfaces import IViewletManager
from megrok import navigation

from horae.layout import _
from horae.layout import interfaces


class BaseMenu(navigation.Menu):
    """ Menu implementation which hides sub menu items which do not have sub items
    """
    grok.baseclass()

    @property
    def items(self):
        items = []
        for item in self.viewlets:
            if not item.submenu:
                items.append(item)
            submenu = component.queryMultiAdapter((self.context, self.request, self.view), interface=IViewletManager, name=item.submenu)
            if submenu is None:
                continue
            submenu.update()
            if submenu.viewlets:
                items.append(item)
        return items


class MainNavigation(BaseMenu):
    """ Main navigation
    """
    grok.implements(interfaces.IMainNavigation)
    grok.name('navigation.main')
    navigation.submenu('menu.global.manage', _(u'Manage site'), order=100)
    cssClass = 'nav nav-main'


class GlobalManageMenu(navigation.Menu):
    """ Global manage menu
    """
    grok.implements(interfaces.IGlobalManageMenu)
    grok.name('menu.global.manage')
    cssClass = 'menu menu-global-manage'


class EditNavigation(BaseMenu):
    """ Edit navigation
    """
    grok.implements(interfaces.IEditNavigation)
    grok.name('navigation.edit')
    navigation.submenu('menu.views', _(u'Views'), order=10)
    navigation.submenu('menu.actions', _(u'Actions'), order=20)
    navigation.submenu('menu.add', _(u'Add'), order=30)
    navigation.submenu('menu.manage', _(u'Manage'), order=40)
    cssClass = 'nav nav-edit'


class ContextualManageMenu(navigation.Menu):
    """ Contextual manage menu
    """
    grok.implements(interfaces.IContextualManageMenu)
    grok.name('menu.manage')
    cssClass = 'menu menu-manage'


class ViewsMenu(navigation.Menu):
    """ Views menu
    """
    grok.implements(interfaces.IViewsMenu)
    grok.name('menu.views')
    cssClass = 'menu menu-views'


class ActionsMenu(navigation.Menu):
    """ Actions menu
    """
    grok.implements(interfaces.IActionsMenu)
    grok.name('menu.actions')
    cssClass = 'menu menu-actions'


class AddMenu(navigation.Menu):
    """ Add menu
    """
    grok.implements(interfaces.IAddMenu)
    grok.name('menu.add')
    cssClass = 'menu menu-add'


class MainActionsMenu(navigation.Menu):
    """ Main actions menu
    """
    grok.implements(interfaces.IMainActionsMenu)
    grok.name('menu.mainactions')
    cssClass = 'mainactions button-group'
    cssItemClass = 'button button-discreet'
