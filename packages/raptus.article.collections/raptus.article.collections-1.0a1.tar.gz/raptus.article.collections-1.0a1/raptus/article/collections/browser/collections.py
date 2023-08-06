from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _p
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.collections.interfaces import ICollections as ICollectionsProvider

class ICollections(interface.Interface):
    """ Marker interface for the collections viewlet
    """

class Component(object):
    """ Component which lists collections of an article
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)

    title = _(u'Collections')
    description = _(u'List of collections and their results contained in the article.')
    image = '++resource++collections.gif'
    interface = ICollections
    viewlet = 'raptus.article.collections'

    def __init__(self, context):
        self.context = context

def _css_class(i, l):
    cls = []
    if i == 0:
        cls.append('first')
    if i == l-1:
        cls.append('last')
    if i % 2 == 0:
        cls.append('odd')
    if i % 2 == 1:
        cls.append('even')
    return ' '.join(cls)

class Viewlet(ViewletBase):
    """ Viewlet listing the collections and their results contained in the article
    """
    index = ViewPageTemplateFile('collections.pt')

    cssClass = 'component componentFull collections'
    component = 'collections'
    type = 'collections'

    def _class(self, brain, i, l):
        return _css_class(i, l)

    @property
    @memoize
    def props(self):
        return getToolByName(self.context, 'portal_properties').raptus_article

    @property
    @memoize
    def results(self):
        return self.props.getProperty('%s_results' % self.type, 10)

    @property
    @memoize
    def date(self):
        return self.props.getProperty('%s_date' % self.type, False)

    @property
    @memoize
    def title(self):
        return self.props.getProperty('%s_title' % self.type, True)

    @property
    @memoize
    def description(self):
        return self.props.getProperty('%s_description' % self.type, True)

    @property
    @memoize
    def more(self):
        return self.props.getProperty('%s_more' % self.type, True)

    @memoize
    def collections(self):
        plone = component.getMultiAdapter((self.context, self.request), name=u'plone')
        provider = ICollectionsProvider(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(provider.getCollections(component=self.component), component=self.component)
        i = 0
        l = len(items)
        collections = []
        for item in items:
            more_link = item['obj'].Schema()['more'].get(item['obj'])
            item.update({'title': item['brain'].Title,
                         'class': self._class(item['brain'], i, l),
                         'description': item['brain'].Description,
                         'url': item['brain'].getURL(),
                         'results': [],
                         'more': False,
                         'more_link': more_link if more_link else _p(u'read_more', default=u'Read More&hellip;')})
            results = item['obj'].queryCatalog()
            limit = self.results
            if item['obj'].getLimitNumber():
                limit = item['obj'].getItemCount()
            rl = min(limit, len(results)) if limit > 0 else len(results)
            ri = 0
            for record in results:
                if limit > 0 and len(item['results']) == limit:
                    item['more'] = self.more
                    break
                result = {'title': record.Title,
                          'class': _css_class(ri, rl),
                          'description': record.Description,
                          'url': record.getURL()}
                if self.date:
                    date = getattr(record, self.date, None)
                    if date is not None:
                        result['date'] = plone.toLocalizedTime(date)
                item['results'].append(result)
                ri += 1
            if len(item['results']):
                collections.append(item)
                i += 1
        return collections

class ICollectionsLeft(interface.Interface):
    """ Marker interface for the collections left viewlet
    """

class ComponentLeft(Component):
    """ Component which lists collections of an article on the left side
    """
    title = _(u'Collections left')
    description = _(u'List of collections and their results contained in the article displayed on the left side.')
    image = '++resource++collections_left.gif'
    interface = ICollectionsLeft
    viewlet = 'raptus.article.collections.left'

class ViewletLeft(Viewlet):
    """ Viewlet listing the collections and their results contained in the article on the left side
    """
    cssClass = 'component componentLeft collections collections-left'
    component = 'collections.left'
    type = 'collections_left'

class ICollectionsRight(interface.Interface):
    """ Marker interface for the collections right viewlet
    """

class ComponentRight(Component):
    """ Component which lists collections of an article on the right side
    """
    title = _(u'Collections right')
    description = _(u'List of collections and their results contained in the article displayed on the right side.')
    image = '++resource++collections_right.gif'
    interface = ICollectionsRight
    viewlet = 'raptus.article.collections.right'

class ViewletRight(Viewlet):
    """ Viewlet listing the collections and their results contained in the article on the right side
    """
    cssClass = 'component componentRight collections collections-right'
    component = 'collections.right'
    type = 'collections_right'

class ICollectionsColumns(interface.Interface):
    """ Marker interface for the collections columns viewlet
    """

class ComponentColumns(Component):
    """ Component which lists collections of an article in columns
    """
    title = _(u'Collections columns')
    description = _(u'List of collections and their results contained in the article displayed in columns.')
    image = '++resource++collections_columns.gif'
    interface = ICollectionsColumns
    viewlet = 'raptus.article.collections.columns'

class ViewletColumns(Viewlet):
    """ Viewlet listing the collections and their results contained in the article in columns
    """
    cssClass = 'component componentFull collections collections-columns'
    component = 'collections.columns'
    type = 'collections_columns'

    @property
    @memoize
    def columns(self):
        return self.props.getProperty('collections_columns', 3)

    def _class(self, brain, i, l):
        i = i % self.columns
        return super(ViewletColumns, self)._class(brain, i, self.columns)
