#!/usr/bin/env python
from setuptools import setup, find_packages


setup(name='tsunami',
      version='0.2',
      description='Web framework based tornado',
      keywords = "web framework tornado",
      author='tsangpo',
      author_email='tsangpozheng@gmail.com',
      url='http://www.tsangpo.net/',

      packages=find_packages(),#['tsunami', 'tsunami.utils', 'tsunami.clients', 'tsunami.runtime'],
      include_package_data=True,
      scripts=['tsunami-create'],

      install_requires=['tornado', 'sqlalchemy', 'werkzeug'],
      provides=['tsunami'],
     )

