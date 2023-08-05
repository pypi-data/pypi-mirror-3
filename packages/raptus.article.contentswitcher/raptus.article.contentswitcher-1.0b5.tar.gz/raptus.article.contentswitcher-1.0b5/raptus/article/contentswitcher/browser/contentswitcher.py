from Acquisition import aq_inner
from zope import interface, component

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.nesting.interfaces import IArticles
from raptus.article.teaser.interfaces import ITeaser

REFERENCE = False
try:
    from raptus.article.reference.interfaces import IReference
    REFERENCE = True
except:
    pass

class IContentSwitcher(interface.Interface):
    """ Marker interface for the content switcher viewlet
    """

class Component(object):
    """ Component which shows a content fader
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Article switcher')
    description = _(u'Article switcher which continually fades in and out the contained articles and provides a tabbed navigation.')
    image = '++resource++contentswitcher.gif'
    interface = IContentSwitcher
    viewlet = 'raptus.article.contentswitcher'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet showing the content switcher
    """
    index = ViewPageTemplateFile('contentswitcher.pt')
    css_class = "componentFull contentswitcher-full full"
    thumb_size = "contentswitcherthumb"
    img_size = "contentswitcher"
    component = "contentswitcher"
    
    @property
    @memoize
    def articles(self):
        provider = IArticles(self.context)
        manageable = interfaces.IManageable(self.context)
        raw_items = manageable.getList(provider.getArticles(component=self.component), self.component)
        items = []
        for item in raw_items:
            img = ITeaser(item['obj'])
            if img.getTeaserURL(self.img_size):
                item.update({'title': item['brain'].Title,
                             'description': item['brain'].Description,
                             'caption': img.getCaption(),
                             'img': img.getTeaser(self.thumb_size),
                             'img_url': img.getTeaserURL(self.img_size),
                             'url': item['brain'].hasDetail and item['brain'].getURL() or None})
                if REFERENCE:
                    reference = IReference(item['obj'])
                    url = reference.getReferenceURL()
                    if url:
                        item['url'] = url
                items.append(item)
        return items

class IContentSwitcherTeaser(interface.Interface):
    """ Marker interface for the content switcher teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which shows a content switcher above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Article switcher teaser')
    description = _(u'Article switcher which continually fades in and out the contained articles, provides a tabbed navigation and is displayed above the columns.')
    image = '++resource++contentswitcher_teaser.gif'
    interface = IContentSwitcherTeaser
    viewlet = 'raptus.article.contentswitcher.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(Viewlet):
    """ Viewlet showing the content switcher
    """
    index = ViewPageTemplateFile('contentswitcher.pt')
    css_class = "componentFull contentswitcher-teaser teaser"
    thumb_size = "contentswitcherthumb"
    img_size = "contentswitcherteaser"
    component = "contentswitcher.teaser"
