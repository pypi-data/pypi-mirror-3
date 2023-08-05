from setuptools import setup, find_packages
import sys, os

version = "0.1.1"

setup(name='clwapp',
      version=version,
      description="Command Line Web APP",
      long_description="""gives the output from a command line application TTW
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@openplans.org',
      url='',
      license="",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = clwapp.factory:factory
      """,
      )
      
