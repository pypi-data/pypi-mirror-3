# -*- coding: UTF-8 -*-
"""
transform .ppt file to HTML
"""

from Products.AROfficeTransforms.config import PLONE_VERSION
from Products.PortalTransforms.interfaces import itransform

from powerpoint_ppthtml import document

import os.path



class ppt_to_html:
    if PLONE_VERSION == 4:
        from zope.interface import implements
        implements(itransform)
    else:
        __implements__ = itransform

    __name__ = "ppt_to_html"
    inputs   = ("application/vnd.ms-powerpoint",)
    output   = "text/html"

    def __init__(self,name=None):
        if name:
            self.__name__=name
    
    def name(self):
        return self.__name__

    def convert(self, data, cache, **kwargs):
        orig_file = kwargs.get('filename') or 'unknown.ppt'

        doc = document(orig_file, data, 'text/html')
        doc.convert()
        convdata = doc.getconverted()

        path, images = doc.subObjects(doc.tmpdir)
        objects = {}
        if images:
            doc.fixImages(path, images, objects)
        doc.cleanDir(doc.tmpdir)

        cache.setData(convdata)
        cache.setSubObjects(objects)
        return cache

def register():
    return ppt_to_html()

def initialize():
    engine = getToolByName(portal, 'portal_transforms')
    engine.registerTransform(register())
