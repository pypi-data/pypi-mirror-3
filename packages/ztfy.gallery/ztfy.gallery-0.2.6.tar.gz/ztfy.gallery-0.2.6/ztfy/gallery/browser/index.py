### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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
import chardet
import codecs
import csv
from cStringIO import StringIO

# import Zope3 interfaces
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.blog.layer import IZTFYBlogBackLayer
from ztfy.gallery.interfaces import IGalleryIndexUploadData, IGalleryContainerTarget, IGalleryContainer, \
                                    IGalleryIndex, IGalleryImage, IGalleryImageExtension, IGalleryImageIndexInfo, \
    IGalleryIndexManager

# import Zope3 packages
from z3c.form import field
from z3c.template.template import getLayoutTemplate, GetLayoutTemplate
from zope.component import adapts
from zope.interface import implements
from zope.traversing import namespace
from zope.traversing.api import getParent
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.skin import BaseDialogAddForm, BaseDialogDisplayForm, BaseDialogEditForm
from ztfy.gallery.browser.gallery import GalleryContainerContentsView
from ztfy.gallery.index import GalleryIndexEntry
from ztfy.skin.menu import JsMenuItem

from ztfy.gallery import _


class GalleryIndexNamespaceTraverser(namespace.view):
    """++index++ namespace"""

    def traverse(self, name, ignored):
        result = IGalleryIndex(self.context, None)
        if result is not None:
            return result
        raise TraversalError('++index++')


class GalleryIndexAddMenuItem(JsMenuItem):
    """Gallery index add menu item"""

    title = _(":: Add gallery index...")


class GalleryIndexAddForm(BaseDialogAddForm):
    """Gallery index add form"""

    title = _("New index")
    legend = _("Adding new gallery index from CSV file")

    fields = field.Fields(IGalleryIndexUploadData)
    layout = getLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = GalleryContainerContentsView
    handle_upload = True

    def createAndAdd(self, data):
        gallery = IGalleryContainer(self.context)
        index = IGalleryIndex(gallery, None)
        if index is not None:
            if data.get('clear'):
                index.clear()
            csv_data = data.get('data')
            encoding = data.get('encoding')
            if not encoding:
                encoding = chardet.detect(csv_data).get('encoding', 'utf-8')
            language = data.get('language')
            csv_data = codecs.getreader(encoding).decode(csv_data)[0].encode('utf-8')
            values = index.values or {}
            if data.get('headers'):
                reader = csv.DictReader(StringIO(csv_data),
                                        delimiter=str(data.get('delimiter')),
                                        quotechar=str(data.get('quotechar')))
                for row in reader:
                    key = unicode(row['id'])
                    entry = values.get(key)
                    if entry is None:
                        entry = GalleryIndexEntry()
                    title = entry.title.copy()
                    title.update({ language: unicode(row.get('title')) })
                    entry.title = title
                    description = entry.description.copy()
                    description.update({ language: unicode(row.get('description')) })
                    entry.description = description
                    values[key] = entry
            else:
                reader = csv.reader(StringIO(csv_data),
                                    delimiter=str(data.get('delimiter')),
                                    quotechar=str(data.get('quotechar')))
                for row in reader:
                    key = unicode(row[0])
                    entry = values.get(key)
                    if entry is None:
                        entry = GalleryIndexEntry()
                    title = entry.title.copy()
                    title.update({ language: unicode(row[1]) })
                    entry.title = title
                    description = entry.description.copy()
                    description.update({ language: unicode(row[2]) })
                    entry.description = description
                    values[key] = entry
            index.values = values


class GalleryIndexContentsView(BaseDialogDisplayForm):
    """Gallery index contents"""

    legend = _("Gallery index contents")


class GalleryImageIndexExtension(object):
    """Gallery image index extension"""

    adapts(IGalleryImage, IZTFYBlogBackLayer)
    implements(IGalleryImageExtension)

    title = _("Index")
    icon = '/--static--/ztfy.gallery.back/img/index.png'
    klass = 'index'
    weight = 10

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def klass(self):
        if IGalleryIndexManager.providedBy(getParent(self.context)):
            return 'index'
        else:
            return 'hidden'

    @property
    def url(self):
        return """javascript:$.ZBlog.dialog.open('%s/@@indexProperties.html')""" % absoluteURL(self.context, self.request)


class GalleryImageIndexEditForm(BaseDialogEditForm):
    """Gallery image index edit form"""

    legend = _("Edit image index properties")

    fields = field.Fields(IGalleryImageIndexInfo)
    layout = GetLayoutTemplate()
    parent_interface = IGalleryContainerTarget
    parent_view = None

    @property
    def widgets_prefix(self):
        return """<div class="image"><img src="%s/++file++image/++display++w800.jpeg" /></div>""" % \
                  absoluteURL(self.context, self.request)
