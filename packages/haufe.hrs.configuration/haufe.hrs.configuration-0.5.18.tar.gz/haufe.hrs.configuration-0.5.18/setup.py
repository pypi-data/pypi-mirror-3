from setuptools import setup, find_packages
import os

version = '0.5.18'

setup(name='haufe.hrs.configuration',
      version=version,
      description='A central configuration service for Zope 2/3-based '+
                  'applications  based on a pseudo-hierarchical ' +
                  'INI-file format with model support for defining the ' +
                  'configuration schema',
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "License :: OSI Approved :: Zope Public License",
        "Intended Audience :: Developers",

        ],
      keywords='Zope Configuration ',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['haufe', 'haufe.hrs'],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[
          'setuptools',
          'zope.event',
          'zope.interface',
          'zope.component',
          'zope.configuration',
          'cfgparse',
          # -*- Extra requirements: -*-
      ],
      tests_require='nose',
      extras_require=dict(test=['zope.testing', 'zope.configuration', 'nose']),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
