from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='pyramid_utils',
      version=version,
      description="Module that adds some plugins to speed up writting pyramid applications",
      long_description="""\
              The module is still really incomplete, there is no possibility to configure it
              and it only adds subscribers at the moment to get context_urls.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Loic Faure-Lacroix',
      author_email='lamerstar@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'pyramid',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
