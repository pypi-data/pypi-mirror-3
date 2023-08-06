"""
Uses the http://sf.net/projects/pdftohtml bin to do its handy work

"""
from Products.AROfficeTransforms.config import PLONE_VERSION
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.commandtransform import popentransform
from Products.CMFDefault.utils import bodyfinder
from transform_libs.double_encoded import noDoubleEncoding
from htmlutils import fixBrokenStyles
import os
from subprocess import Popen
process_double_encoding = False

class popen_pdf_to_html(popentransform):
    if PLONE_VERSION == 4:
        from zope.interface import implements
        implements(itransform)
    else:
        __implements__ = itransform

    __version__ = '2004-07-02.01'

    __name__ = "pdf_to_html"
    inputs   = ('application/pdf',)
    output  = 'text/html'
    output_encoding = 'utf-8'

    binaryName = "pdftohtml"
    binaryArgs = "%(infile)s -noframes -c -stdout -enc UTF-8"
    useStdin = False

    def getData(self, couterr):
        return bodyfinder(couterr.read())

class pdf_to_html(commandtransform):
    __implements__ = itransform

    __name__ = "pdf_to_html"
    inputs   = ('application/pdf',)
    output  = 'text/html'
    output_encoding = 'utf-8'

    binaryName = "pdftohtml"
    binaryArgs = "-noframes -c -enc UTF-8"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        if 'filename' not in kwargs or not kwargs['filename']:
            kwargs['filename'] = 'unknown.pdf'
        
        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        html = self.invokeCommand(tmpdir, fullname)
        html = fixBrokenStyles(html)
        if process_double_encoding :
            html = noDoubleEncoding(html)

        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(bodyfinder(html).decode('utf-8','replace').encode('utf-8'))
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        if os.name=='posix':
            cmd = 'cd "%s" && %s %s "%s" 2>error_log 1>/dev/null' % (
                   tmpdir, self.binary, self.binaryArgs, fullname)
        else:
            cmd = 'cd "%s" && %s %s "%s"' % (
                  tmpdir, self.binary, self.binaryArgs, fullname)
        p = Popen(cmd, shell = True)
        sts = os.waitpid(p.pid, 0)

        try:
            htmlfilename = os.path.join(tmpdir, sansext(fullname) + '.html')
            htmlfile = open(htmlfilename, 'r')
            html = htmlfile.read()
            htmlfile.close()
        except:
            try:
                return open("%s/error_log" % tmpdir, 'r').read()
            except:
                return "transform failed while running %s (maybe this pdf file doesn't support transform)" % cmd
        return html

def register():
    return pdf_to_html()
