from __future__ import nested_scopes

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from utils import input_file_path, output_file_path, normalize_html,\
     load, matching_inputs
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.interfaces import idatastream
from Products.MimetypesRegistry.MimeTypesTool import MimeTypesTool
from Products.PortalTransforms.TransformEngine import TransformTool

from Products.PortalTransforms.libtransforms.utils import MissingBinary

#transforms test
from Products.AROfficeTransforms.transforms.pdf_to_html import pdf_to_html
from Products.AROfficeTransforms.transforms.word_to_html import word_to_html
from Products.AROfficeTransforms.transforms.oo2_to_html import oo2_to_html
from Products.AROfficeTransforms.transforms.ooo_to_html import ooo_to_html
from Products.AROfficeTransforms.transforms.word_to_text import word_to_text

from os.path import exists
import sys
# we have to set locale because lynx output is locale sensitive !
os.environ['LC_ALL'] = 'C'

class TransformTest(ATSiteTestCase):

    def do_convert(self, filename=None):
        if filename is None and exists(self.output + '.nofilename'):
            output = self.output + '.nofilename'
        else:
            output = self.output
        input = open(self.input)
        orig = input.read()
        input.close()
        data = datastream(self.transform.name())
        res_data = self.transform.convert(orig, data, filename=filename)
        self.assert_(idatastream.providedBy(res_data))
        got = res_data.getData()
        try:
            output = open(output)
        except IOError:
            import sys
            print >>sys.stderr, 'No output file found.'
            print >>sys.stderr, 'File %s created, check it !' % self.output
            output = open(output, 'w')
            output.write(got)
            output.close()
            self.assert_(0)
        expected = output.read()
        print self.normalize
        if self.normalize is not None:
            expected = self.normalize(expected)
            got = self.normalize(got)
        output.close()

        self.assertEquals(got, expected,
                          '[%s]\n\n!=\n\n[%s]\n\nIN %s(%s)' % (
            got, expected, self.transform.name(), self.input))
        self.assertEquals(self.subobjects, len(res_data.getSubObjects()),
                          '%s\n\n!=\n\n%s\n\nIN %s(%s)' % (
            self.subobjects, len(res_data.getSubObjects()), self.transform.name(), self.input))

    def testSame(self):
        self.do_convert(filename=self.input)

    def testSameNoFilename(self):
        self.do_convert()

    def __repr__(self):
        return self.transform.name()

TRANSFORMS_TESTINFO = (
    ('Products.AROfficeTransforms.transforms.pdf_to_html',
     "unknown.pdf", "unknown.html", normalize_html, 2
     ),
    ('Products.AROfficeTransforms.transforms.oo2_to_html',
     "test_sxw.sxw", "test_sxw.html", normalize_html, 1
     ),
    ('Products.AROfficeTransforms.transforms.oo2_to_html',
     "test_sxc.sxc", "test_sxc.html", normalize_html, 0
     ),
    ('Products.AROfficeTransforms.transforms.oo2_to_html',
     "test_sxi.sxi", "test_sxi.html", normalize_html, 1
     ),
    ('Products.AROfficeTransforms.transforms.ooo_to_html',
     "test_odt.odt", "test_odt.html", normalize_html, 1
     ),
    ('Products.AROfficeTransforms.transforms.ooo_to_html',
     "test_ods.ods", "test_ods.html", normalize_html, 0
     ),
    ('Products.AROfficeTransforms.transforms.ooo_to_html',
     "test_odp.odp", "test_odp.html", normalize_html, 1
     ),
    ('Products.AROfficeTransforms.transforms.ppt_to_html',
     "test_ppt.ppt", "test_ppt.html", normalize_html, 0
     ),
    ('Products.AROfficeTransforms.transforms.word_to_html',
     "test_doc.doc", "test_doc.html", normalize_html, 1
     ),
    ('Products.AROfficeTransforms.transforms.word_to_text',
     "test_doc.doc", "test_doc.txt", normalize_html , 0
     ),
    )

def initialise(transform, normalize, pattern):
    global TRANSFORMS_TESTINFO
    for fname in matching_inputs(pattern):
        outname = '%s.out' % fname.split('.')[0]
        #print transform, fname, outname
        TRANSFORMS_TESTINFO += ((transform, fname, outname, normalize, 0),)


TR_NAMES = None

def make_tests(test_descr=TRANSFORMS_TESTINFO):
    """generate tests classes from test info

    return the list of generated test classes
    """
    tests = []
    for _transform, tr_input, tr_output, _normalize, _subobjects in test_descr:
        # load transform if necessary
        if type(_transform) is type(''):
            try:
                _transform = load(_transform).register()
            except MissingBinary:
                # we are not interessted in tests with missing binaries
                continue
            except:
                import traceback
                traceback.print_exc()
                continue

        if TR_NAMES is not None and not _transform.name() in TR_NAMES:
            print 'skip test for', _transform.name()
            continue

        class TransformTestSubclass(TransformTest):
            input = input_file_path(tr_input)
            output = output_file_path(tr_output)
            transform = _transform
            normalize = lambda x, y: _normalize(y)
            subobjects = _subobjects

        tests.append(TransformTestSubclass)

    return tests


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in make_tests():
        suite.addTest(makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
