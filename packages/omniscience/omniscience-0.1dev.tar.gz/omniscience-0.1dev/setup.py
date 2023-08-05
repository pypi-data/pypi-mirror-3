from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='omniscience',
      version=version,
      description="Enables dynamic real-time monitoring/logging of code.",
      long_description="""\
Enables dynamic real-time monitoring/logging of code.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='logging real-time realtime dynamic framework decorators',
      author='Gabriel Krupa',
      author_email='omniscience@bluekelp.com',
      url='',
      license='TBD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
