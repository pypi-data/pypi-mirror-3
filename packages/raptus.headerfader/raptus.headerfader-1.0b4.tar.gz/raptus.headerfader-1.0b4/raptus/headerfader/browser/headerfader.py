from random import choice
from Acquisition import aq_inner, aq_parent

from zope.component import getMultiAdapter

from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from Products.ATContentTypes.interface.image import IATImage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from raptus.header.browser.viewlets import HeaderViewlet
from raptus.header.interfaces import IHeader

class HeaderFaderViewlet(HeaderViewlet):
    index = ViewPageTemplateFile('headerfader.pt')

    @property
    @memoize
    def images(self):
        images = []
        header = self.header()
        if not header or self.disabled:
            return
        brains = self.catalog(object_provides=IATImage.__identifier__,
                              path={'query': header.getPath(),'depth': 1})
        if not len(brains):
            return
        random = choice(brains)
        w = self.props.getProperty('header_width', 0)
        h = self.props.getProperty('header_height', 0)
        for brain in brains:
            obj = brain.getObject()
            scales = getMultiAdapter((obj, self.request), name='images')
            scale = scales.scale('image',
                                 width=(w and w or 1000000),
                                 height=(h and h or 1000000))
            if scale is None:
                continue
            images.append({'image': scale.url,
                           'title': brain.Title,
                           'description': brain.Description,
                           'current': brain is random})
        images.sort(cmp=lambda x,y: (x['current'] and -1 or 0))
        return images

    update = ViewletBase.update
    render = ViewletBase.render
