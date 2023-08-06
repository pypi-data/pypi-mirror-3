import unittest
from zope.testing import doctestunit

modules = (
    'Products.AROfficeTransforms.transforms.ooo_to_html',
    )

def test_suite():
    return unittest.TestSuite(
        [doctestunit.DocTestSuite(module=module) for module in modules]
        )
