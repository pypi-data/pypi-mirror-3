from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.app',
      version=version,
      description="Provides the Horae resource planning system as a Grok application",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Simon Kaeser',
      author_email='skaeser@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['horae'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grok',
          'grokui.admin',
          'grokcore.startup',
          # -*- Extra requirements: -*-
          'zope.i18n[compile]',
          'horae.auth',
          'horae.core',
          'horae.properties',
          'horae.search',
          'horae.ticketing',
      ],
      entry_points="""
      [paste.app_factory]
      main = grokcore.startup:application_factory
      """,
      )
