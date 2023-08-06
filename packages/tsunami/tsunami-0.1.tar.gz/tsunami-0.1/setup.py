#!/usr/bin/env python
from setuptools import setup, find_packages


setup(name='tsunami',
      version='0.1',
      description='Web framework based tornado',
      keywords = "web framework tornado",
      author='tsangpo',
      author_email='tsangpozheng@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',

      packages=find_packages(),#['tsunami', 'tsunami.utils', 'tsunami.clients', 'tsunami.runtime'],
      include_package_data=True,
      scripts=['tsunami_create'],

      requires=['sqlalchemy', 'werkzeug'],
      provides=['tsunami'],
     )

