# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


readme = open('README.rst').read()
license = open('LICENSE').read()

setup(
    name='django-pipeline',
    version='1.2.7',
    description='Pipeline is an asset packaging library for Django.',
    long_description=readme,
    author='Timothée Peignier',
    author_email='timothee.peignier@tryphon.org',
    url='https://github.com/cyberdelia/django-pipeline',
    license=license,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
