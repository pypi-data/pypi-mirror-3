# -*- coding: UTF-8 -*-
"""
transform OOo file to HTML through XSL
"""
from Products.AROfficeTransforms.config import PLONE_VERSION
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils \
    import sansext
from Products.PortalTransforms.libtransforms.commandtransform \
    import commandtransform
import os
from subprocess import Popen

XSL_STYLESHEET = os.path.join(
  os.getcwd(), os.path.dirname(__file__), 'transform_libs/sx2ml', 'main_html.xsl')

class ooo_to_html(commandtransform):
    if PLONE_VERSION == 4:
        from zope.interface import implements
        implements(itransform)
    else:
        __implements__ = itransform

    __name__ = 'ooo_to_html'
    inputs = ('application/vnd.sun.xml.writer',
              'application/vnd.sun.xml.impress',
              'application/vnd.sun.xml.calc',
              )
    output = 'text/html'

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = kwargs.get('filename') or 'unknown_sxw.sxw'
        
        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        html = self.invokeCommand(tmpdir, fullname)
        
        subObjectsPaths = [tmpdir, os.path.join(tmpdir, 'Pictures')]
        for subObjectsPath in subObjectsPaths:
            if os.path.exists(subObjectsPath):
                path, images = self.subObjects(subObjectsPath)
                objects = {}
                if images:
                    self.fixImages(path, images, objects)
        
        self.cleanDir(tmpdir)
        cache.setData(html)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        cmd = 'cd "%s" && unzip %s 2>error_log 1>/dev/null' % (
            tmpdir, fullname)
        p = Popen(cmd, shell = True)
        sts = os.waitpid(p.pid, 0)

        cmd = ('cd "%s" && xsltproc --novalid %s content.xml >"%s.html" '
            '2>"%s.log-xsltproc"') % (
            tmpdir, XSL_STYLESHEET, sansext(fullname), sansext(fullname))
        p = Popen(cmd, shell = True)
        sts = os.waitpid(p.pid, 0)

        try:
            htmlfile = open(os.path.join(tmpdir, "%s.html" % sansext(fullname)),
                            'r')
            html = htmlfile.read()
            htmlfile.close()
        except:
            try:
                return open(os.path.join(tmpdir, 'error_log'), 'r').read()
            except:
                return ''
        return html

def register():
    return ooo_to_html()

def initialize():
    engine = getToolByName(portal, 'portal_transforms')
    engine.registerTransform(register())
    
