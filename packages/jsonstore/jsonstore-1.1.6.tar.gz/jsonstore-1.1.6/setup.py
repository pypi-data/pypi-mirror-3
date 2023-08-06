from setuptools import setup, find_packages
import sys, os

version = '1.1.6'

setup(name='jsonstore',
      version=version,
      description="A RESTful exposed database for arbitrary JSON objects.",
      long_description="""\
A schema-free database for JSON documents, exposed through a REST API, with searching implemented using a flexible matching algorithm that has support for standard and user-defined operators.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://pypi.python.org/pypi/jsonstore',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'Paste',
          'PasteScript',
          'PasteDeploy',
          'WebOb',
          'simplejson',
          'uuid',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = jsonstore.rest:make_app

      [paste.paster_create_template]
      jsonstore = jsonstore.template:JsonstoreTemplate
      """,
      )
      
