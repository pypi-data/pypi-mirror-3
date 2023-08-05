from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.search',
      version=version,
      description="Provides searching functionality for the Horae resource planning system",
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
          # -*- Extra requirements: -*-
          'zc.catalog',
          'hurry.query',
          'horae.auth',
          'horae.autocomplete',
          'horae.cache',
          'horae.core',
          'horae.layout',
          'horae.lifecycle',
          'horae.properties',
          'horae.ticketing',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
