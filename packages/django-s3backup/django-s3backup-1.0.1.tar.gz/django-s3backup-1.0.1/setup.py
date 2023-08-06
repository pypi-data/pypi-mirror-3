#!/usr/bin/env python
 
from setuptools import setup

readme = open('README.rst').read()

setup(
    name='django-s3backup',
    version='1.0.1',
    description="A django app to backup database dumps to an S3 bucket",
    long_description=readme,
    author='Tino de Bruijn',
    author_email='tinodb@gmail.com',
    packages=['s3backup'],
    url='https://bitbucket.org/tino/django-s3backup/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    install_requires=['boto >=2.1.1', 'path.py >=2.2.2']
)