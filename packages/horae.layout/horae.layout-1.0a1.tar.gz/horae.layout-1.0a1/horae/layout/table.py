import grok
import math
from hashlib import sha1

from zope import interface
from zope.session.interfaces import ISession
from zope.catalog.catalog import ResultSet

from horae.layout import _
from horae.layout import interfaces
from horae.layout.layout import namespace

grok.templatedir('templates')


def default_row_factory(object, columns, request):
    item = {}
    for column in columns:
        item[column] = object.get(column, u'')
    return item


class Table(grok.View):
    """ A generic table which handles paging and sorting
    """
    grok.context(interface.Interface)
    grok.implements(interfaces.ITable)

    def __init__(self, *args, **kw):
        super(Table, self).__init__(*args, **kw)
        self.base_url = self.url(self.context) + '/table'
        self.columns = []
        self.footer = []
        self.sortable = None
        self.filterable = None
        self.rows = []
        self.page_size = 20
        self.page = 1
        self.pages = 0
        self.sort = None
        self.reverse = False
        self.caption = None
        self.session_key = None
        self.session = ISession(self.request)
        self.row_factory = default_row_factory
        self.css_class = u''

    def namespace(self):
        return namespace(self.request)

    def set_session_key(self, key):
        self._session_key = key

    def get_session_key(self):
        if not self._session_key:
            return sha1(self.base_url).hexdigest()
        return self._session_key
    session_key = property(get_session_key, set_session_key)

    def set_session(self, name, value):
        self.session[self.session_key][name] = value

    def get_session(self, name, default=None):
        return self.session[self.session_key].get(name, default)

    def reset(self):
        """ Resets paging, sorting and filtering
        """
        for key in self.session[self.session_key].keys():
            del self.session[self.session_key][key]

    def sorting(self):
        """ Returns the desired sorting and whether to reverse the sort order
        """
        if self.sortable is None:
            return None, False

        sort = self.request.get(self.session_key + '.sort', None)
        if sort is not None:
            if sort in self.sortable.values():
                self.set_session('sort', sort)
            if sort == 'reset':
                self.set_session('sort', None)

        reverse = self.request.get(self.session_key + '.reverse', None)
        if reverse is not None:
            self.set_session('reverse', reverse == '1')
        return self.get_session('sort', None), self.get_session('reverse', False)

    def filtering(self):
        """ Returns the desired filters (list of name, value tuples)
        """
        if self.filterable is None:
            return None
        filter = self.request.get(self.session_key + '.filter', {})
        filterit = self.request.get(self.session_key + '.filterit', None)
        available = self.filterable.keys()
        if filterit is not None:
            filtering = []
            for column, value in filter.items():
                if column in available:
                    filtering.append((column, [self.filterable[column].getTermByToken(token).value for token in value]))
            self.set_session('filter', filtering)
        return self.get_session('filter', None)

    def update(self):
        self.sort, self.reverse = self.sorting()
        self.total = len(self.rows)
        if self.page_size is None:
            self.page_size = self.total
        self.pages = self.total > 0 and int(math.ceil(self.total / float(self.page_size))) or 0

        page = self.request.get(self.session_key + '.page', None)
        if page is not None:
            self.set_session('page', int(page))
        self.page = int(max(1, min(self.pages, self.get_session('page', 0))))

        # Page zapper
        self.page_links = []
        if self.pages > 1:
            if self.page > 3:
                self.page_links.append({'url': self.base_url + '?' + self.session_key + '.page=1',
                                        'label': u'&laquo;',
                                        'class': 'first',
                                        'title': _(u'Go to first page')})
            if self.page > 0:
                self.page_links.append({'url': self.base_url + '?' + self.session_key + '.page=' + str(self.page - 1),
                                        'label': u'&lsaquo;',
                                        'class': 'previous',
                                        'title': _(u'Go to previous page')})
            if self.page > 3:
                self.page_links.append({'label': u'&hellip;'})
            for p in range(max(1, self.page - 2), min(self.pages + 1, self.page + 3)):
                self.page_links.append({'url': not p == self.page and self.base_url + '?' + self.session_key + '.page=' + str(p) or None,
                                        'label': str(p),
                                        'class': p == self.page and 'current' or None})
            if self.pages - self.page > 2:
                self.page_links.append({'label': u'&hellip;'})
            if self.pages - self.page > 0:
                self.page_links.append({'url': self.base_url + '?' + self.session_key + '.page=' + str(self.page + 1),
                                        'label': u'&rsaquo;',
                                        'class': 'next',
                                        'title': _(u'Go to next page')})
            if self.pages - self.page > 2:
                self.page_links.append({'url': self.base_url + '?' + self.session_key + '.page=' + str(self.pages),
                                        'label': u'&raquo;',
                                        'class': 'last',
                                        'title': _(u'Go to last page')})

        # Columns
        self.column_links = []
        self.column_names = []
        for name, column in self.columns:
            self.column_names.append(name)
            link = {'name': name,
                    'class': 'column-' + name,
                    'title': column}
            if self.sortable is not None and name in self.sortable:
                index = self.sortable[name]
                link['class'] += ' sortable' + (self.sort == index and (self.reverse and ' sorted reversed' or ' sorted') or '')
                link['url'] = self.base_url + '?' + self.session_key + '.sort=' + (self.sort == index and self.reverse and 'reset' or index) + '&' + self.session_key + '.reverse=' + (self.sort == index and not self.reverse and '1' or '0') + '#' + self.session_key
            self.column_links.append(link)

        # Rows
        self.data = []
        self.start = int(self.page_size * (self.page - 1))
        self.end = min(self.total, int(self.page_size * self.page))
        if isinstance(self.rows, ResultSet):
            page = []
            i = 0
            for uid in self.rows.uids:
                if i >= self.start:
                    page.append(self.rows.uidutil.getObject(uid))
                i += 1
                if i >= self.end:
                    break
        else:
            page = self.rows[self.start:self.end]
        for row in page:
            self.data.append(self.row_factory(row, self.column_names, self.request))

        # Reduce filterable
        self.selected_filters = {}
        if self.filterable is not None:
            filterable = {}
            for column, vocab in self.filterable.items():
                if not column in self.column_names or \
                   not len(vocab):
                    continue
                filterable[column] = vocab
            self.filterable = filterable
            filter = self.filtering()
            if filter is not None:
                self.selected_filters = dict(filter)

        self.action = self.request.getURL() + '#' + self.session_key

        self.start += 1

        self.tfoot = [[{'colspan': colspan,
                        'content': content} for colspan, content in row] for row in self.footer]
