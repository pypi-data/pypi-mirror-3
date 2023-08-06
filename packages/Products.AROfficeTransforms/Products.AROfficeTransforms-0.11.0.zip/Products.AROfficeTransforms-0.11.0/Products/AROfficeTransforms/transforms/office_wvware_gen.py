# -*- coding: UTF-8 -*-
"""
transform doc file to HTML or TEXT
"""
import re, tempfile
import os, os.path
from os.path import join as pjoin
from subprocess import Popen
from Products.PortalTransforms.libtransforms.utils import bin_search, \
     sansext, bodyfinder, scrubHTML
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform

from Products.AROfficeTransforms import logger
from Products.AROfficeTransforms.transforms import utils

xmltag = '<?xml version="1.0" encoding="utf-8"?>\n'

mimecmdmap = {
    'text/plain': "wvText",
    'text/html': "wvHtml",
}

mimeoptmap = {
    'text/plain': "",
    'text/html': "--charset=utf-8",
}

mimeextmap = {
    'text/plain': "txt",
    'text/html': "html",
}


class document(commandtransform):

    def __init__(self, name, data, outmime):
        """ Initialization: create tmp work directory and copy the
        document into a file"""
        self.outmime = outmime
        commandtransform.__init__(self, name, binary=mimecmdmap[outmime])
        name = self.name()
        if not name.endswith('.doc'):
            name = name + ".doc"
        self.tmpdir, self.fullname = self.initialize_tmpdir(data, filename = name)

    def convert(self):
        "Convert the document"
        tmpdir = self.tmpdir

        # for windows, install wvware from GnuWin32 at C:\Program Files\GnuWin32\bin
        # you can use:
        # wvware.exe -c ..\share\wv\wvHtml.xml --charset=utf-8 -d d:\temp d:\temp\test.doc > test.html
        timelimit = utils.timelimit()

        if os.name == 'posix':
            command = 'cd "%s" && %s %s %s "%s" "%s.%s"' % (
              tmpdir, timelimit, self.binary, mimeoptmap[self.outmime], self.fullname,
              self.__name__, mimeextmap[self.outmime],)
            logger.info(command)
            p = Popen(command,
                      shell=True)
            sts = os.waitpid(p.pid, 0)

    def _html(self):
        htmlfile = open(pjoin(self.tmpdir, self.__name__+".html"), 'r')
        html = htmlfile.read()
        htmlfile.close()
        #html = scrubHTML(html)
        body = bodyfinder(html)
        body = xmltag + body
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
