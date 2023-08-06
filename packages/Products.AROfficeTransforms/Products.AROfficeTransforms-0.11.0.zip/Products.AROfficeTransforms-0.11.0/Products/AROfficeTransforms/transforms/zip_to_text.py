# -*- coding: UTF-8 -*-
"""
transform zip files to Text through the zipfile library
"""
from Products.AROfficeTransforms.config import PLONE_VERSION
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
import zipfile
from string import join

class zip_to_text(commandtransform):
    if PLONE_VERSION == 4:
        from zope.interface import implements
        implements(itransform)
    else:
        __implements__ = itransform

    __name__ = "zip_to_text"
    inputs   = ("application/zip","application/x-zip-compressed")
    output   = "text/plain"

    def __init__(self,name=None):
        if name:
            self.__name__=name
    
    def name(self):
        return self.__name__

    def convert(self, data, cache, **kwargs):
        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        try:
            zip = zipfile.ZipFile(fullname,'r')
            data = join(zip.namelist(), "\n")
            data = data.decode('cp850', "replace").encode('utf-8', "replace")
        except:
            return "transform from %s failed (maybe this zip file is corrupted)" % fullname
        
        self.cleanDir(tmpdir)
        cache.setData(data)
        return cache

def register():
    return zip_to_text()

def initialize():
    engine = getToolByName(portal, 'portal_transforms')
    engine.registerTransform(register())
