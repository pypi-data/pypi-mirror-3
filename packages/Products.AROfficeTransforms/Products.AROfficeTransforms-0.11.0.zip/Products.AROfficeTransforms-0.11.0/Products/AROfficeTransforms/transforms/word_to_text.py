# -*- coding: UTF-8 -*-
"""
transform .doc file to Text through WVWare
"""
from Products.AROfficeTransforms.config import PLONE_VERSION
from Products.PortalTransforms.interfaces import itransform
from office_wvware_gen import document
import os.path

class word_to_text:
    if PLONE_VERSION == 4:
        from zope.interface import implements
        implements(itransform)
    else:
        __implements__ = itransform

    __name__ = "word_to_text"
    inputs   = ("application/msword",)
    output   = "text/plain"

    def __init__(self,name=None):
        if name:
            self.__name__=name
    
    def name(self):
        return self.__name__

    def convert(self, data, cache, **kwargs):
        orig_file = kwargs.get('filename') or 'unknown.doc'

        doc = document(orig_file, data, 'text/plain')
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
    return word_to_text()

def initialize():
    engine = getToolByName(portal, 'portal_transforms')
    engine.registerTransform(register())
