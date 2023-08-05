from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.dashboard',
      version=version,
      description="Provides a dashboard for Horae",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
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
          'fanstatic',
          'zope.fanstatic',
          # -*- Extra requirements: -*-
          'horae.auth',
          'horae.autocomplete',
          'horae.core',
          'horae.datetime',
          'horae.layout',
          'horae.lifecycle',
          'horae.properties',
          'horae.ticketing',
          'horae.timeaware',
      ],
      entry_points={
          'fanstatic.libraries': [
              'horae.dashboard = horae.dashboard.resource:library',
          ]
      })
