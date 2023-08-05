import grok

from zope.interface import Interface
from fanstatic import Library, Resource

from js.jquery import jquery
from js import jqueryui

from horae.datetime import resource

from horae.layout import _
from horae.layout import interfaces

library = Library('horae.layout', 'static')

uitheme = Resource(library, 'uitheme/jquery-ui.css')
reset = Resource(library, 'reset.css')
deco = Resource(library, 'deco.css')
typography = Resource(library, 'typography.css', depends=[reset, uitheme, ])
editor = Resource(library, 'editor.css', depends=[typography, ])
style = Resource(library, 'style.css', depends=[deco, typography, ])
form = Resource(library, 'form.css')
listing = Resource(library, 'listing.css')
nestedliststyle = Resource(library, 'nestedlist.css')
jqplot = Resource(library, 'jqplot.css')

initialization = Resource(library, 'initialization.js', [jquery, ])
i18n = Resource(library, 'i18n.js', depends=[jquery, ])
hours = Resource(library, 'hours.js', depends=[resource.css, resource.spinbox, initialization, ])
collapsible = Resource(library, 'collapsible.js', depends=[jquery, initialization, ])
search = Resource(library, 'search.js', depends=[collapsible, initialization, ])
nestedlist = Resource(library, 'nestedlist.js', depends=[collapsible, initialization, i18n])
hash = Resource(library, 'hash.js', depends=[jquery, ])
dialogs = Resource(library, 'dialogs.js', depends=[i18n, initialization, ])
ticketing = Resource(library, 'ticketing.js', depends=[i18n, initialization, ])
listing_js = Resource(library, 'listing.js', depends=[initialization, ])


@grok.adapter(Interface, name='horae.layout.style.css')
@grok.implementer(interfaces.IResourceProvider)
def style_resource_provider(context):
    """ Provides CSS resources for the basic horae layout
    """
    return [style, form, listing, nestedliststyle, jqplot, ]


# This is here solely to have it captured by i18ndude
_(u'More')


@grok.adapter(Interface, name='horae.layout.ticketing.js')
@grok.implementer(interfaces.IResourceProvider)
def ticketing_resource_provider(context):
    """ Provides JavaScript resources for ticket specific functionality
    """
    return [ticketing, ]


@grok.adapter(Interface, name='horae.layout.listing.js')
@grok.implementer(interfaces.IResourceProvider)
def listing_resource_provider(context):
    """ Provides JavaScript resources for listing specific functionality
    """
    return [listing_js, ]


@grok.adapter(Interface, name='horae.layout.dialogs.js')
@grok.implementer(interfaces.IResourceProvider)
def dialogs_resource_provider(context):
    """ Provides JavaScript resources for displaying dialogs
    """
    return [dialogs, ]


@grok.adapter(Interface, name='horae.layout.hours.js')
@grok.implementer(interfaces.IResourceProvider)
def hours_resource_provider(context):
    """ Provides JavaScript resources for synchronization between a
        date/time field and an hours field
    """
    return [hours, ]


@grok.adapter(Interface, name='horae.layout.search.js')
@grok.implementer(interfaces.IResourceProvider)
def search_resource_provider(context):
    """ Provides JavaScript resources for search specific functionality
    """
    return [search, ]


@grok.adapter(Interface, name='horae.layout.hash.js')
@grok.implementer(interfaces.IResourceProvider)
def hash_resource_provider(context):
    """ Provides JavaScript resources for adjusting page scroll position
        if a hash is present
    """
    return [hash, ]


@grok.adapter(Interface, name='horae.layout.jqueryui')
@grok.implementer(interfaces.IResourceProvider)
def jqueryui_resource_provider(context):
    """ Provides the jQuery UI library
    """
    return [jqueryui.jqueryui, uitheme, ]
