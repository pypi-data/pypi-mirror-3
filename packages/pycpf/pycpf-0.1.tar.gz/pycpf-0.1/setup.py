from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pycpf',
      version=version,
      description="CPF generation and validation",
      long_description=open('readme.rst').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='cpf validation generation',
      author='Umgeher Taborda, Diogo Baeder',
      author_email='umgeher@mitgnu.com',
      url='https://bitbucket.org/umgeher/pycpf',
      license='BSD 2-clause',
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
