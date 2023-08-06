from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='raptus.portlet.multilanguage',
      version=version,
      description="Provides a static text portlet for which one may select the language for which the portlet is available",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Raptus AG',
      author_email='dev@raptus.com',
      url='https://svn.plone.org/svn/collective/raptus.portlet.multilanguage',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['raptus', 'raptus.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.portlet.static',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
