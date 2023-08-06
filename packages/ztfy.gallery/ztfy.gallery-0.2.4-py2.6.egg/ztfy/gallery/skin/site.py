### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
from persistent import Persistent

# import Zope3 interfaces
from hurry.query.interfaces import IQuery
from z3c.json.interfaces import IJSONWriter
from z3c.language.switch.interfaces import II18n
from zope.annotation.interfaces import IAnnotations
from zope.catalog.interfaces import ICatalog
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces import NotFound
from zope.session.interfaces import ISession

# import local interfaces
from interfaces import IHomeBackgroundManager
from interfaces import ISiteManagerPresentationInfo, ISiteManagerPresentation
from layer import IGalleryLayer
from ztfy.blog.browser.interfaces.skin import IPresentationTarget
from ztfy.blog.interfaces.category import ICategorizedContent
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.file.interfaces import IImageDisplay
from ztfy.workflow.interfaces import IWorkflowContent

# import Zope3 packages
from hurry.query import And
from hurry.query.set import AnyOf
from hurry.query.value import Eq
from zope.component import adapts, getUtility, queryMultiAdapter, queryUtility
from zope.container.contained import Contained
from zope.interface import implements, Interface
from zope.location import locate
from zope.proxy import ProxyBase, setProxiedObject
from zope.publisher.browser import BrowserPage
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser import absoluteURL

# import local packages
from menu import GallerySkinJsMenuItem
from ztfy.blog.browser.site import BaseSiteManagerIndexView
from ztfy.blog.defaultskin.site import SiteManagerRssView as BaseSiteManagerRssView
from ztfy.file.property import ImageProperty
from ztfy.skin.page import TemplateBasedPage
from ztfy.utils.catalog.index import Text

from ztfy.gallery import _


SITE_MANAGER_PRESENTATION_KEY = 'ztfy.gallery.presentation'


class SiteManagerPresentationViewMenuItem(GallerySkinJsMenuItem):
    """Site manager presentation menu item"""

    title = _(" :: Presentation model...")


class SiteManagerPresentation(Persistent, Contained):
    """Site manager presentation infos"""

    implements(ISiteManagerPresentation)

    site_icon = ImageProperty(ISiteManagerPresentation['site_icon'])
    site_logo = ImageProperty(ISiteManagerPresentation['site_logo'])
    site_watermark = ImageProperty(ISiteManagerPresentation['site_watermark'])
    news_blog_oid = FieldProperty(ISiteManagerPresentation['news_blog_oid'])
    news_entries = FieldProperty(ISiteManagerPresentation['news_entries'])
    reports_blog_oid = FieldProperty(ISiteManagerPresentation['reports_blog_oid'])
    footer_section_oid = FieldProperty(ISiteManagerPresentation['footer_section_oid'])
    facebook_app_id = FieldProperty(ISiteManagerPresentation['facebook_app_id'])
    disqus_site_id = FieldProperty(ISiteManagerPresentation['disqus_site_id'])

    @property
    def news_blog(self):
        if not self.news_blog_oid:
            return None
        intids = getUtility(IIntIds)
        return intids.queryObject(self.news_blog_oid)

    @property
    def reports_blog(self):
        if not self.reports_blog_oid:
            return None
        intids = getUtility(IIntIds)
        return intids.queryObject(self.reports_blog_oid)

    @property
    def footer_section(self):
        if not self.footer_section_oid:
            return None
        intids = getUtility(IIntIds)
        return intids.queryObject(self.footer_section_oid)


class SiteManagerPresentationAdapter(ProxyBase):

    adapts(ISiteManager)
    implements(ISiteManagerPresentation)

    def __init__(self, context):
        annotations = IAnnotations(context)
        presentation = annotations.get(SITE_MANAGER_PRESENTATION_KEY)
        if presentation is None:
            presentation = annotations[SITE_MANAGER_PRESENTATION_KEY] = SiteManagerPresentation()
            locate(presentation, context, '++presentation++')
        setProxiedObject(self, presentation)


class SiteManagerPresentationTargetAdapter(object):

    adapts(ISiteManager, IGalleryLayer)
    implements(IPresentationTarget)

    target_interface = ISiteManagerPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class SiteManagerIndexView(BaseSiteManagerIndexView):
    """Site manager index page"""

    @property
    def background_image(self):
        manager = IHomeBackgroundManager(self.context, None)
        if manager is not None:
            return manager.getImage()

    @property
    def categories(self):
        catalog = queryUtility(ICatalog, 'Catalog')
        if catalog is not None:
            index = catalog.get('categories')
            if index is not None:
                intids = getUtility(IIntIds)
                return sorted(((id, intids.queryObject(id)) for id in index.values()),
                              key=lambda x: II18n(x[1]).queryAttribute('shortname', request=self.request))
        return []

    @property
    def reports(self):
        target = self.presentation.reports_blog
        if (target is not None) and target.visible:
            return target.getVisibleTopics()[:4]
        else:
            return []

    @property
    def news(self):
        target = self.presentation.news_blog
        if (target is not None) and target.visible:
            return target.getVisibleTopics()[:self.presentation.news_entries]
        else:
            return []

    def getCategory(self, topic):
        categories = ICategorizedContent(topic).categories
        if not categories:
            return ''
        return ' - '.join(('<a href="%s">%s</a>' % (absoluteURL(category, self.request),
                                                    II18n(category).queryAttribute('shortname', request=self.request)) for category in categories))


class SiteManagerRssView(BaseSiteManagerRssView):

    @property
    def topics(self):
        result = []
        target = self.presentation.reports_blog
        if (target is not None) and target.visible:
            result.extend(target.getVisibleTopics())
        target = self.presentation.news_blog
        if (target is not None) and target.visible:
            result.extend(target.getVisibleTopics())
        result.sort(key=lambda x: IWorkflowContent(x).publication_effective_date, reverse=True)
        return result[:self.presentation.news_entries + 4]


class SiteManagerBackgroundURL(BrowserPage):

    def __call__(self):
        writer = getUtility(IJSONWriter)
        image = self.background_image
        if image is not None:
            display = IImageDisplay(image.image).getDisplay('w1024')
            if display is not None:
                return writer.write({ 'url': absoluteURL(display, self.request),
                                      'title': II18n(image).queryAttribute('title', request=self.request) })
        return writer.write('none')

    @property
    def background_image(self):
        manager = IHomeBackgroundManager(self.context, None)
        if manager is not None:
            return manager.getImage()


SITE_MANAGER_SESSION_ID = 'ztfy.gallery.site.search'

class SiteManagerSearchView(TemplateBasedPage):
    """Site manager search page"""

    def __call__(self):
        form = self.request.form
        if 'page' in form:
            session = ISession(self.request)[SITE_MANAGER_SESSION_ID]
            self.search_text = search_text = session.get('search_text', '')
            self.search_tag = search_tag = session.get('search_tag', '') or None
        else:
            self.search_text = search_text = form.get('search_text', '').strip()
            self.search_tag = search_tag = form.get('search_tag', '') or None
        if not search_text:
            if not search_tag:
                self.request.response.redirect(absoluteURL(self.context, self.request))
                return ''
            else:
                intids = getUtility(IIntIds)
                category = intids.queryObject(search_tag)
                self.request.response.redirect(absoluteURL(category, self.request))
                return ''
        return super(SiteManagerSearchView, self).__call__()

    def update(self):
        super(SiteManagerSearchView, self).update()
        query = getUtility(IQuery)
        params = []
        params.append(Eq(('Catalog', 'content_type'), 'ITopic'))
        params.append(Text(('Catalog', 'title'), { 'query': ' '.join(('%s*' % m for m in self.search_text.split())),
                                                   'autoexpand': 'on_miss',
                                                   'ranking': True }))
        if self.search_tag:
            intids = getUtility(IIntIds)
            self.category = intids.queryObject(self.search_tag)
            params.append(AnyOf(('Catalog', 'categories'), (self.search_tag,)))
        # get search results
        results = sorted((topic for topic in query.searchResults(And(*params))
                                          if IWorkflowContent(topic).isVisible()),
                         key=lambda x: IWorkflowContent(x).publication_effective_date,
                         reverse=True)
        # store search settings in session
        session = ISession(self.request)[SITE_MANAGER_SESSION_ID]
        session['search_text'] = self.search_text
        session['search_tag'] = self.search_tag
        # handle pagination
        page = int(self.request.form.get('page', 0))
        page_length = 10
        first = page_length * page
        last = first + page_length - 1
        pages = len(results) / page_length
        if len(results) % page_length:
            pages += 1
        self.results = { 'results': results[first:last + 1],
                         'pages': pages,
                         'first': first,
                         'last': last,
                         'has_prev': page > 0,
                         'has_next': last < len(results) - 1 }


class SiteManagerIconView(BrowserPage):
    """'favicon.ico' site view"""

    def __call__(self):
        icon = ISiteManagerPresentation(self.context).site_icon
        if icon is not None:
            view = queryMultiAdapter((icon, self.request), Interface, 'index.html')
            if view is not None:
                return view()
        raise NotFound(self.context, 'favicon.ico', self.request)
