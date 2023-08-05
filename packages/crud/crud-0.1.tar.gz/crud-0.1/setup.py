from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='crud',
      version=version,
      description="CRUD operations for wsgi applications",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='CRUD WSGI admin mongo ming sprox toscawidgets sqlalchemy',
      author='Chris Perkins',
      author_email='chris@percious.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
