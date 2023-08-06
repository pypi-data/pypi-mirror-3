#!/usr/bin/env python
from distutils.core import setup

version='1.0.0'

setup(
    name='smartresponder',
    version=version,
    author='Valentin Gorbunov',
    author_email='valuerr@gmail.com',

    packages=['smartresponder'],

    url='http://bitbucket.org/valuerr/smartresponder/',
    license = 'MIT license',
    description = "smartresponder.ru API wrapper",

    long_description = open('README.rst').read() + open('CHANGES.rst').read(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
