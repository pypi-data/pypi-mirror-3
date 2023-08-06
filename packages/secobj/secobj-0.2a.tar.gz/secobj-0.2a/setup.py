# coding: utf-8
from setuptools import setup, find_packages
import sys, os

version = '0.2'

def read(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

setup(name='secobj',
      version=version,
      description="ACL security for functions and classes",
      long_description=read("README.rst"),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries",
      ],
      keywords='acl authorization security access',
      author='Marc Göldner',
      author_email='info@cramren.de',
      url='https://github.com/cramren/secobj',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite='tests',
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
