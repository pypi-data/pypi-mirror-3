#!/usr/bin/env python
from setuptools import setup, find_packages


setup(name='appsample',
      version='0.1',
      description='web app based tsunami',
      keywords = "appsample web",
      author='tsangpo',
      author_email='tsangpozheng@gmail.com',
      url='http://projects.tsangpo.net/appsample/',

      packages=find_packages(),
      include_package_data=True,
      scripts=['appsample.py'],

      requires=['tsunami', 'psycopg2'],
      provides=['appsample'],
     )

