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
from interfaces import IGalleryImage, IGalleryContainer, IGalleryContainerTarget

# import Zope3 packages
from zope.component import adapts
from zope.container.contained import Contained
from zope.interface import implements
from zope.location import locate
from zope.proxy import ProxyBase, setProxiedObject
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.blog.ordered import OrderedContainer
from ztfy.extfile.blob import BlobImage
from ztfy.file.property import ImageProperty
from ztfy.i18n.property import I18nTextProperty


class GalleryImage(Persistent, Contained):

    implements(IGalleryImage)

    title = I18nTextProperty(IGalleryImage['title'])
    description = I18nTextProperty(IGalleryImage['description'])
    credit = FieldProperty(IGalleryImage['credit'])
    image = ImageProperty(IGalleryImage['image'], klass=BlobImage, img_klass=BlobImage)
    image_id = FieldProperty(IGalleryImage['image_id'])
    visible = FieldProperty(IGalleryImage['visible'])


class GalleryContainer(OrderedContainer):

    implements(IGalleryContainer)

    def getVisibleImages(self):
        return [img for img in self.values() if img.visible]


GALLERY_ANNOTATIONS_KEY = 'ztfy.gallery.container'

class GalleryContainerAdapter(ProxyBase):
    """Gallery container adapter"""

    adapts(IGalleryContainerTarget)
    implements(IGalleryContainer)

    def __init__(self, context):
        annotations = IAnnotations(context)
        container = annotations.get(GALLERY_ANNOTATIONS_KEY)
        if container is None:
            container = annotations[GALLERY_ANNOTATIONS_KEY] = GalleryContainer()
            locate(container, context, '++gallery++')
        setProxiedObject(self, container)
