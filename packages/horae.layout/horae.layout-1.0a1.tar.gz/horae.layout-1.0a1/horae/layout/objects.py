import grok

from zope import component
from zope.formlib.widget import renderElement

from horae.layout import _
from horae.layout import layout
from horae.layout import interfaces

grok.templatedir('templates')


class ObjectOverview(layout.View):
    """ Generic view listing objects meant to be subclassed by specific implementations.
    """
    grok.baseclass()
    grok.require('horae.Manage')
    grok.template('overview')

    actions_template = u'<div class="button-group">%(actions)s</div>'
    button_template = u'<a href="%(url)s" class="button button-discreet %(cssClass)s">%(label)s</a> '

    # To be provided by subclass
    columns = []
    container_iface = None
    label = _(u'Objects')

    def row_factory(self, object, columns, request):
        row = {}
        row['actions'] = ''
        providers = []
        for name, provider in component.getAdapters((object, self,), interfaces.IObjectTableActionsProvider):
            providers.append(provider)
        for name, provider in component.getAdapters((object,), interfaces.IObjectTableActionsProvider):
            providers.append(provider)
        providers.sort(key=lambda p: getattr(p, 'order', 0))
        for provider in providers:
            for action in provider.actions(self.request):
                row['actions'] += self.button_template % action
        if row['actions']:
            row['actions'] = self.actions_template % dict(actions=row['actions'])
        for name, extender in component.getAdapters((self,), interfaces.IObjectOverviewExtender):
            extender.row_factory(row, object, columns, request)
        return row

    def add(self):
        raise NotImplementedError(u'concrete classes must implement add()')

    def get_table(self, resources):
        table = component.getMultiAdapter((self.context, self.request), name='table')
        table.page_size = None
        table.columns = self.columns
        if not ('actions', '') in table.columns:
            table.columns.append(('actions', ''))
        table.sortable = {}
        table.row_factory = self.row_factory
        table.base_url = self.url(self.context)
        table.rows = resources
        for name, extender in component.getAdapters((self,), interfaces.IObjectOverviewExtender):
            extender.get_table(table)
        return table

    def objects(self):
        return list(self.container.objects())

    def update(self):
        super(ObjectOverview, self).update()
        self.types = []
        self.back = self.url(self.context)
        self.container = self.container_iface(self.context)
        self.table = self.get_table(self.objects())()


class ObjectFormMixin(object):
    """ Mix in class for object forms
    """

    # To be provided by subclass
    overview = ''
    dynamic_fields = True
    id_attr = 'id'

    def __call__(self, plain=False, selector=None, id=None):
        self.object = self.context.get_object(id)
        if self.object is not None:
            if self.dynamic_fields:
                self.form_fields = grok.AutoFields(self.object.__class__).omit('id')
            self.additional = renderElement('input',
                                            type='hidden',
                                            name='id',
                                            value=getattr(self.object, self.id_attr))
        else:
            self.redirect(self.cancel_url())
        return super(ObjectFormMixin, self).__call__(plain, selector)

    def cancel_url(self):
        return self.url(self.context.__parent__) + '/' + self.overview

    def next_url(self, obj=None):
        return self.cancel_url()


class EditObject(ObjectFormMixin, layout.EditForm):
    """ Generic object edit form meant to be subclassed by specific implementations
    """
    grok.baseclass()
    grok.require('horae.Manage')

    def setUpWidgets(self, ignore_request=False):
        self.context, context = self.object, self.context
        super(EditObject, self).setUpWidgets(ignore_request)
        self.context = context

    def apply(self, **data):
        self.applyData(self.object, **data)


class DeleteObject(ObjectFormMixin, layout.DeleteForm):
    """ Generic object delete form meant to be subclassed by specific implementations
    """
    grok.baseclass()
    grok.require('horae.Manage')
    dynamic_fields = False

    def item_title(self):
        return self.object.name

    def delete(self):
        self.context.del_object(self.object.id)
