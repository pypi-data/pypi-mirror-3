#!/usr/bin/env python

'''
Created on 17 Jul 2011

@author: oracal
'''
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='cineworld',
    version='0.1.0',
    author='Thomas Whitton',
    author_email='mail@thomaswhitton.com',
    packages=['cineworld'],
    url='https://github.com/oracal/cineworld',
    license='LICENSE.txt',
    description='Cineworld API Wrapper',
    long_description='cineworld offers an easy-to-use Python wrapper to interact with the Cineworld API(https://www.cineworld.co.uk/developer/api/cinemas). Before you try and use the API, make sure you sign up to get an API Key'
)
