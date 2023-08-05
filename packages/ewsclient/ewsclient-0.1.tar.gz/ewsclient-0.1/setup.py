from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='ewsclient',
      version=version,
      description="Client for Microsoft Exchange Web Services",
      long_description="""\
Minimal hacks to access Exchange web services through suds.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Daniel Holth',
      author_email='dholth@gmail.com',
      url='http://bitbucket.org/dholth/ewsclient',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'suds',
          'python-ntlm',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
