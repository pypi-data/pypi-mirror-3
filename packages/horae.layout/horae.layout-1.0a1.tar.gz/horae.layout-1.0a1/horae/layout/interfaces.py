import grok

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope import interface

from megrok.navigation import interfaces


class IHoraeBrowserLayer(IDefaultBrowserLayer):
    """ Horae browser layer
    """
    grok.skin('default')


class IViewView(interface.Interface):
    """ Marker interface for default views
    """


class IDisplayView(interface.Interface):
    """ Marker interface for display views
    """


class IEditView(interface.Interface):
    """ Marker interface for edit views
    """


class IAddForm(IEditView):
    """ Basic add form
    """

    def object_type():
        """ Display name of the object to be created
        """

    def next_url(obj):
        """ Returns the url to be redirected to after successful creation
        """

    def cancel_url():
        """ Returns the url to be redirected to after cancellation
        """

    def create(**data):
        """ Returns the object to be added
        """

    def add(obj):
        """ Adds the created object to the specified container
        """

    def apply(obj, **data):
        """ Applies the data to the added object
        """


class IEditForm(IEditView):
    """ Basic edit form
    """

    def next_url():
        """ Returns the url to be redirected to after successful edition
        """

    def cancel_url():
        """ Returns the url to be redirected to after cancellation
        """

    def apply(**data):
        """ Applies the data to the object
        """


class IDeleteForm(IEditView):
    """ Basic delete form
    """

    def item_title():
        """ Returns the title of the object to be deleted
        """

    def next_url():
        """ Returns the url to be redirected to after successful deletion
        """

    def cancel_url():
        """ Returns the url to be redirected to after cancellation
        """

    def delete():
        """ Deletes the object
        """


class IRow(interface.Interface):
    """ A table row
    """

    def get(name):
        """ Returns the data for the specific column
        """


class ITable(interface.Interface):
    """ A generic table which handles paging and sorting
    """

    base_url = interface.Attribute('base_url',
        """ The url to base paging and sorting links on
        """
    )
    columns = interface.Attribute('columns',
        """ A list of name, title tuples defining the available columns
        """
    )
    footer = interface.Attribute('footer',
        """ A list of lists of colspan, content tuples forming the rows of the table footer
        """
    )
    sortable = interface.Attribute('sortable',
        """ A dict having column names as key and the sortable index name as value defining the
            columns to be sortable, by default no columns are sortable
        """
    )
    filterable = interface.Attribute('filterable',
        """ A dictionary mapping column names to the vocabulary defining the available values
            for filtering, by default no columns are filterable
        """
    )
    rows = interface.Attribute('rows',
        """ A list of objects providing IRow holding the data of the rows
        """
    )
    page_size = interface.Attribute('page_size',
        """ The number of rows to be displayed on a page
        """
    )
    page = interface.Attribute('page',
        """ The current page to be displayed
        """
    )
    pages = interface.Attribute('pages',
        """ The number of available pages
        """
    )
    caption = interface.Attribute('caption',
        """ The caption of the table
        """
    )
    session_key = interface.Attribute('session_key',
        """ The session key used to store the paging and sorting,
            by default a hash of the base_url is used
        """
    )
    row_factory = interface.Attribute('row_factory',
        """ A callable taking the object, a list of columns and the request as parameters
            and returns a dict holding the data for the row
            (see horae.core.table.default_row_factory)
        """
    )
    css_class = interface.Attribute('css_class',
        """ Additional css class to be set on the form wrapped around the table
        """
    )

    def reset():
        """ Resets paging, sorting and filtering
        """

    def sorting():
        """ Returns the desired sorting and whether to reverse the sort order
        """

    def filtering():
        """ Returns the desired filters (list of name, value tuples)
        """

    def __call__():
        """ Renders the table
        """


class IMainNavigation(interfaces.IMenu):
    """ Main navigation
    """


class IEditNavigation(interfaces.IMenu):
    """ Edit navigation
    """


class IGlobalManageMenu(interfaces.IMenu):
    """ Global manage menu
    """


class IContextualManageMenu(interfaces.IMenu):
    """ Contextual manage menu
    """


class IViewsMenu(interfaces.IMenu):
    """ Views menu
    """


class IActionsMenu(interfaces.IMenu):
    """ Actions menu
    """


class IMainActionsMenu(interfaces.IMenu):
    """ Main actions menu
    """


class IAddMenu(interfaces.IMenu):
    """ Add menu
    """


class IObjectTableActionsProvider(interface.Interface):
    """ Provider for actions displayed in the object overview table
    """

    order = interface.Attribute('controls ordering of actions')

    def actions(request):
        """ List of dictionaries with the following keys:

             * label
             * url
             * cssClass
        """


class IResourceProvider(interface.Interface):
    """ A provider for fanstatic resources to be included in any horae.layout view
    """

    def __iter__():
        """ The fanstatic resources to be included
        """


class IViewExtender(interface.Interface):
    """ An adapter extending any view
    """

    def pre_update():
        """ Called before the views update is called
        """

    def pre_setUpWidgets(ignore_request=False):
        """ Called before the forms setUpWidgets is called
        """

    def post_update():
        """ Called after the views update is called
        """

    def apply(obj, **data):
        """ Called when applying changes to an object
        """

    def validate(action, data):
        """ Called when validating a form
        """


class IObjectOverviewExtender(interface.Interface):
    """ An adapter extending ObjectOverview views
    """

    def get_table(self, table):
        """ Modifies the table
        """

    def row_factory(self, row, object, columns, request):
        """ Modifies the row
        """


class IBreadcrumbs(interface.Interface):
    """ Adapter making an object visible in the breadcrumbs
    """

    permission = interface.Attribute('permission', 'The permission required to see the item')
    name = interface.Attribute('name', 'The name to be displayed in the breadcrumbs')
    url = interface.Attribute('url', 'The url to be used in the breadcrumbs')
