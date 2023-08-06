from setuptools import setup, find_packages
import os

version = '0.7b5'

setup(name='wildcard.pdfpal',
      version=version,
      description="PDF Thumbnail generation, OCR indexing and extra views integrated with plone.app.async",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='pdf plone thumbnail ocr async',
      author='Nathan Van Gheem',
      author_email='nathan.vangheem@wildcardcorp.com',
      url='http://pypi.python.org/pypi/wildcard.pdfpal',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wildcard'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
	      'lxml'
      ],
      tests_require=[
        'plone.app.testing',
        'unittest2'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
