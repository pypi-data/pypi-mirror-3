from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.properties',
      version=version,
      description="Provides the dynamic property infrastructure used by the Horae resource planning system",
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
          'z3c.relationfield',
          'horae.auth',
          'horae.autocomplete',
          'horae.cache',
          'horae.core',
          'horae.layout',
          'horae.lifecycle',
          'horae.timeaware',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
