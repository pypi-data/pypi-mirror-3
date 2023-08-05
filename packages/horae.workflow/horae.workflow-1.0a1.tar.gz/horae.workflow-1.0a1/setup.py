from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='horae.workflow',
      version=version,
      description="",
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
          # -*- Extra requirements: -*-
          'hurry.workflow',
          'horae.auth',
          'horae.autocomplete',
          'horae.cache',
          'horae.core',
          'horae.layout',
          'horae.properties',
          'horae.search',
          'horae.ticketing',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
