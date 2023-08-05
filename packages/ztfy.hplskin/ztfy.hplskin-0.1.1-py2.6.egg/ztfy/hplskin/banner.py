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
from zope.app.file.interfaces import IImage
from zope.annotation.interfaces import IAnnotations
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.blog.browser.interfaces.container import IActionsColumn, IContainerTableViewActionsCell
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.blog.layer import IZTFYBlogLayer
from ztfy.hplskin.interfaces import IBannerImage, ITopBannerImageAddFormMenuTarget, \
                                    ILeftBannerImageAddFormMenuTarget, IBannerManager, \
                                    IBannerManagerContentsView

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.table.column import Column
from z3c.template.template import getLayoutTemplate
from zope.app.file.image import Image
from zope.component import adapts, getAdapter, queryAdapter, queryMultiAdapter, getUtility
from zope.container.contained import Contained
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.intid.interfaces import IIntIds
from zope.location import locate
from zope.proxy import setProxiedObject, ProxyBase
from zope.publisher.browser import BrowserPage
from zope.security.proxy import removeSecurityProxy
from zope.traversing import namespace, api as traversing_api
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.container import OrderedContainerBaseView
from ztfy.blog.browser.skin import BaseDialogAddForm
from ztfy.blog.ordered import OrderedContainer
from ztfy.file.property import ImageProperty
from ztfy.hplskin.menu import HPLSkinMenuItem, HPLSkinJsMenuItem
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.hplskin import _


class BannerManager(OrderedContainer):
    """Banner manager"""

    implements(IBannerManager)


BANNER_MANAGER_ANNOTATIONS_KEY = 'ztfy.hplskin.banner.%s'

class BannerManagerAdapter(ProxyBase):

    adapts(ISiteManager)
    implements(IBannerManager)

    def __init__(self, context, name):
        annotations = IAnnotations(context)
        banner_key = BANNER_MANAGER_ANNOTATIONS_KEY % name
        manager = annotations.get(banner_key)
        if manager is None:
            manager = annotations[banner_key] = BannerManager()
            locate(manager, context, '++banner++%s' % name)
        setProxiedObject(self, manager)


class BannerManagerNamespaceTraverser(namespace.view):
    """++banner++ namespace"""

    def traverse(self, name, ignored):
        site = getParent(self.context, ISiteManager)
        if site is not None:
            manager = queryAdapter(site, IBannerManager, name)
            if manager is not None:
                return manager
        raise TraversalError('++banner++')


class BannerManagerContentsView(OrderedContainerBaseView):
    """Banner manager contents view"""

    implements(IBannerManagerContentsView)

    interface = IBannerImage

    @property
    def values(self):
        adapter = getAdapter(self.context, IBannerManager, self.name)
        if adapter is not None:
            return removeSecurityProxy(adapter).values()
        return []

    @ajax.handler
    def ajaxRemove(self):
        oid = self.request.form.get('id')
        if oid:
            intids = getUtility(IIntIds)
            target = intids.getObject(int(oid))
            parent = traversing_api.getParent(target)
            del parent[traversing_api.getName(target)]
            return "OK"
        return "NOK"

    @ajax.handler
    def ajaxUpdateOrder(self):
        adapter = getAdapter(self.context, IBannerManager, self.name)
        self.updateOrder(adapter)


class IBannerManagerPreviewColumn(Interface):
    """Marker interface for resource container preview column"""

class BannerManagerPreviewColumn(Column):
    """Resource container preview column"""

    implements(IBannerManagerPreviewColumn)

    header = u''
    weight = 5
    cssClasses = { 'th': 'preview',
                   'td': 'preview' }

    def renderCell(self, item):
        image = IImage(item.image, None)
        if image is None:
            return u''
        return '''<img src="%s/++display++64x64.jpeg" alt="%s" />''' % (absoluteURL(image, self.request),
                                                                        traversing_api.getName(image))


class BannerManagerContentsViewActionsColumnCellAdapter(object):

    adapts(IBannerImage, IZTFYBlogLayer, IBannerManagerContentsView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column
        self.intids = getUtility(IIntIds)

    @property
    def content(self):
        klass = "ui-workflow ui-icon ui-icon-trash"
        result = '''<span class="%s" title="%s" onclick="$.ZBlog.form.remove(%d, this);"></span>''' % (klass,
                                                                                                       translate(_("Delete image"), context=self.request),
                                                                                                       self.intids.register(self.context))
        return result


#
# Top banner custom classes extensions
#

class TopBannerManagerAdapter(BannerManagerAdapter):

    def __init__(self, context):
        super(TopBannerManagerAdapter, self).__init__(context, 'top')


class TopBannerContentsMenuItem(HPLSkinMenuItem):
    """TopBanner contents menu item"""

    title = _("Top banner")


class TopBannerContentsView(BannerManagerContentsView):
    """TopBanner manager contents view"""

    implements(ITopBannerImageAddFormMenuTarget)

    legend = _("Top banner images")
    name = 'top'


#
# Left banner custom classes extensions
#

class LeftBannerManagerAdapter(BannerManagerAdapter):

    def __init__(self, context):
        super(LeftBannerManagerAdapter, self).__init__(context, 'left')


class LeftBannerContentsMenuItem(HPLSkinMenuItem):
    """LeftBanner contents menu item"""

    title = _("Left banner")


class LeftBannerContentsView(BannerManagerContentsView):
    """TopBanner manager contents view"""

    implements(ILeftBannerImageAddFormMenuTarget)

    legend = _("Left banner images")
    name = 'left'


#
# Banner images management
#

class BannerImage(Persistent, Contained):
    """Banner image"""

    implements(IBannerImage)

    image = ImageProperty(IBannerImage['image'], klass=Image, img_klass=Image)


class BannerImageAddMenuItem(HPLSkinJsMenuItem):
    """Banner image add menu"""

    title = _(":: Add image...")


class BannerImageAddForm(BaseDialogAddForm):
    """Banner image add form"""

    title = _("New banner image")
    legend = _("Adding new image")

    fields = field.Fields(IBannerImage)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager
    handle_upload = True

    def create(self, data):
        return BannerImage()

    def add(self, image):
        data = self.request.form.get('form.widgets.image')
        filename = None
        if hasattr(data, 'filename'):
            filename = translateString(data.filename, escapeSlashes=True, forceLower=False, spaces='-')
            if filename in self.context:
                index = 2
                name = '%s-%d' % (filename, index)
                while name in self.context:
                    index += 1
                    name = '%s-%d' % (filename, index)
                filename = name
        if not filename:
            index = 1
            filename = 'image-%d' % index
            while filename in self.context:
                index += 1
                filename = 'image-%d' % index
        self.context[filename] = image


class TopBannerImageAddForm(BannerImageAddForm):

    parent_view = TopBannerContentsView


class LeftBannerImageAddForm(BannerImageAddForm):

    parent_view = LeftBannerContentsView


class BannerImageIndexView(BrowserPage):
    """Banner image default view"""

    def __call__(self):
        return queryMultiAdapter((self.context.image, self.request), Interface, 'index.html')()
