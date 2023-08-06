from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.nesting.interfaces import IArticles

TEASER = False
try:
    from raptus.article.teaser.interfaces import ITeaser
    TEASER = True
except:
    pass

REFERENCE = False
try:
    from raptus.article.reference.interfaces import IReference
    REFERENCE = True
except:
    pass

class ISupersized(interface.Interface):
    """ Marker interface for the supersized viewlet
    """

class Component(object):
    """ Component which shows a supersizedslider of the articles
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)

    title = _(u'Supersized')
    description = _(u'Supersized slider of the articles contained in the article.')
    image = '++resource++supersized.gif'
    interface = ISupersized
    viewlet = 'raptus.article.supersized'

    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet showing the supersizedslider of the articles
    """
    type = 'supersized'
    index = ViewPageTemplateFile('supersized.pt')
    css_class = "supersized-content componentFull"
    thumb_size = "supersized"
    component = "supersized"

    @property
    @memoize
    def props(self):
        return getToolByName(self.context, 'portal_properties').raptus_article

    @property
    @memoize
    def description(self):
        return self.props.getProperty('%s_description' % self.type, False)

    @property
    @memoize
    def arrownav(self):
        return self.props.getProperty('%s_arrownav' % self.type, False)

    @property
    @memoize
    def progressbar(self):
        return self.props.getProperty('%s_progressbar' % self.type, False)

    @property
    @memoize
    def thumbnav(self):
        return self.props.getProperty('%s_thumbnav' % self.type, False)

    @property
    @memoize
    def controlbar(self):
        return self.props.getProperty('%s_controlbar' % self.type, False)

    @property
    @memoize
    def playpause(self):
        return self.props.getProperty('%s_playpause' % self.type, False)

    @property
    @memoize
    def slidecounter(self):
        return self.props.getProperty('%s_slidecounter' % self.type, False)

    @property
    @memoize
    def slidecaption(self):
        return self.props.getProperty('%s_slidecaption' % self.type, False)

    @property
    @memoize
    def thumbstray(self):
        return self.props.getProperty('%s_thumbstray' % self.type, False)

    @property
    @memoize
    def slidelist(self):
        return self.props.getProperty('%s_slidelist' % self.type, False)


    @property
    @memoize
    def image(self):
        if not TEASER:
            return False
        return self.props.getProperty('%s_image' % self.type, False)

    @memoize
    def articles(self):
        provider = IArticles(self.context)
        manageable = interfaces.IManageable(self.context)
        items = provider.getArticles(component=self.component)
        items = manageable.getList(items, self.component)
        i = 0
        l = len(items)
        for item in items:
            item.update({'title': item['brain'].Title,
                         'description': self.description and item['brain'].Description or None,
                         'url': item['brain'].hasDetail and item['brain'].getURL() or None,
                         'class': item.has_key('show') and item['show'] and 'hidden' or ''})
            if REFERENCE:
                reference = IReference(item['obj'])
                url = reference.getReferenceURL()
                if url:
                    item['url'] = url
            if self.image:
                teaser = ITeaser(item['obj'])
                image = {'img': teaser.getTeaserURL(self.thumb_size),
                         'thumb': teaser.getTeaserURL(size="supersizedthumb"),
                         'caption': teaser.getCaption(),
                         'rel': 'supersized'}
                item['image'] = image
            i += 1
        return items

class ISupersizedTeaser(interface.Interface):
    """ Marker interface for the supersizedslider teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows a supersizedslider of the articles displayed above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)

    title = _(u'Supersized Teaser')
    description = _(u'Supersized slider of the articles contained in the article displayed above the columns.')
    image = '++resource++supersized_teaser.gif'
    interface = ISupersizedTeaser
    viewlet = 'raptus.article.supersized.teaser'

    def __init__(self, context):
        self.context = context

class ViewletTeaser(Viewlet):
    """ Viewlet showing the supersizedslider of the images displayed above the columns
    """
    type = 'supersizedteaser'
    css_class = "supersized-teaser componentFull"
    thumb_size = "supersizedteaser"
    component = "supersized.teaser"
