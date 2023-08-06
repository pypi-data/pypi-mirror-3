from setuptools import setup, find_packages
import os

version = '0.11.0'

setup(name='Products.AROfficeTransforms',
      version=version,
      description="Plone module to add conversion from office format to HTML in portal_transforms tool",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone transforms',
      author='atReal',
      author_email='contact@atreal.fr',
      url='http://svn.plone.org/svn/collective/Products.AROfficeTransforms/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
