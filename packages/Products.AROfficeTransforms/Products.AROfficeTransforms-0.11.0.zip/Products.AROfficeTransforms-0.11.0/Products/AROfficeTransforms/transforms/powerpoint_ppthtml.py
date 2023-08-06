# -*- coding: UTF-8 -*-
"""
transform .ppt file to HTML
core converter
"""
import re, tempfile
import os, os.path
from os.path import join as pjoin
from subprocess import Popen
from transform_libs.double_encoded import noDoubleEncoding
from Products.PortalTransforms.libtransforms.utils import bin_search, \
     sansext, bodyfinder, scrubHTML
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
#ppthtml adds its own signature, that may break output encoding
process_double_encoding = True

mimecmdmap = {
    'text/plain': "ppthtml",
    'text/html': "ppthtml",
}

mimeextmap = {
    'text/plain': "txt",
    'text/html': "html",
}

class document(commandtransform):

    def __init__(self, name, data, outmime):
        """ Initialization: create tmp work directory and copy the
        document into a file"""
        self.outmime=outmime
        commandtransform.__init__(self, name, binary=mimecmdmap[outmime])
        name = self.name()
        if not name.endswith('.ppt'):
            name = name + ".ppt"
        self.tmpdir, self.fullname = self.initialize_tmpdir(data, filename=name)

    def convert(self):
        "Convert the document"
        tmpdir = self.tmpdir

        if os.name == 'posix':
            p = Popen('cd "%s" && %s "%s" > "%s.%s"' % (tmpdir, self.binary,
                                                             self.fullname,
                                                             self.__name__,
                                                             mimeextmap[self.outmime],),
                      shell = True)
            sts = os.waitpid(p.pid, 0)


    def _html(self):
        htmlfile = open(pjoin(self.tmpdir, self.__name__+".html"), 'r')
        html = htmlfile.read()
        if process_double_encoding:
            html = noDoubleEncoding(html)
        htmlfile.close()
        html = scrubHTML(html)
        body = bodyfinder(html)
        return body
    
    def _text(self):
        txtfile = open(pjoin(self.tmpdir, self.__name__+".txt"), 'r')
        text = txtfile.read()
        txtfile.close()
        return text
    
    def getconverted(self):
        mimeoutmap= {
            'text/plain': self._text,
            'text/html':  self._html,
        }
        return mimeoutmap[self.outmime]()
