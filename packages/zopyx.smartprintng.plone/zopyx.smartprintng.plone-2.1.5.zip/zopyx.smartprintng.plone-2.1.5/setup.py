from setuptools import setup, find_packages
import os

version = '2.1.5'

setup(name='zopyx.smartprintng.plone',
      version=version,
      description="Produce & Publisher server integration with Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx', 'zopyx.smartprintng'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'BeautifulSoup',
          'zopyx.smartprintng.client',
          'lxml',
          'uuid',
          'Pillow',
          'archetypes.schemaextender',
          'unittest2'
          # -*- Extra requirements: -*-
      ],
      tests_require=['zope.testing'],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
