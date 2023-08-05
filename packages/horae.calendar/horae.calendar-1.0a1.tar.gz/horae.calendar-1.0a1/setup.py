from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.calendar',
      version=version,
      description="Provides generic calendar views (month, week and day) using horae.timeaware",
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
          'horae.core',
          'horae.layout',
      ],
      entry_points={
          'fanstatic.libraries': [
              'horae.calendar = horae.calendar.resource:library',
          ]
      })
