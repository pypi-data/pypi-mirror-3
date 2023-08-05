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
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from interfaces import ITopicPresentation, ITopicPresentationInfo
from layer import IGalleryLayer
from ztfy.blog.browser.interfaces.skin import IPresentationTarget
from ztfy.blog.interfaces.topic import ITopic

# import Zope3 packages
from zope.container.contained import Contained
from zope.component import adapts
from zope.interface import implements
from zope.proxy import ProxyBase, setProxiedObject
from zope.schema.fieldproperty import FieldProperty

# import local packages
from menu import GallerySkinJsMenuItem
from ztfy.i18n.property import I18nTextProperty

from ztfy.gallery import _


TOPIC_PRESENTATION_KEY = 'ztfy.gallery.presentation'


class TopicPresentationViewMenuItem(GallerySkinJsMenuItem):
    """Topic presentation menu item"""

    title = _(" :: Presentation model...")


class TopicPresentation(Persistent, Contained):
    """Topic presentation infos"""

    implements(ITopicPresentation)

    publication_date = I18nTextProperty(ITopicPresentation['publication_date'])
    header_format = FieldProperty(ITopicPresentation['header_format'])
    display_googleplus = FieldProperty(ITopicPresentation['display_googleplus'])
    display_fb_like = FieldProperty(ITopicPresentationInfo['display_fb_like'])
    illustration_position = FieldProperty(ITopicPresentation['illustration_position'])
    illustration_width = FieldProperty(ITopicPresentation['illustration_width'])
    linked_resources = FieldProperty(ITopicPresentation['linked_resources'])


class TopicPresentationAdapter(ProxyBase):

    adapts(ITopic)
    implements(ITopicPresentation)

    def __init__(self, context):
        annotations = IAnnotations(context)
        presentation = annotations.get(TOPIC_PRESENTATION_KEY)
        if presentation is None:
            presentation = annotations[TOPIC_PRESENTATION_KEY] = TopicPresentation()
        setProxiedObject(self, presentation)


class TopicPresentationTargetAdapter(object):

    adapts(ITopic, IGalleryLayer)
    implements(IPresentationTarget)

    target_interface = ITopicPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request
