#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='mailsnake',
    version='1.5.0',
    description='MailChimp API v1.3, STS, Export, Mandrill wrapper for Python.',
    long_description=open('README.rst').read(),
    author='John-Kim Murphy',
    url='https://github.com/michaelhelmick/python-mailsnake',
    packages=find_packages(),
    download_url='http://pypi.python.org/pypi/mailsnake/',
    keywords='mailsnake mailchimp api wrapper export mandrill sts 1.3',
    zip_safe=True,
    install_requires=['simplejson', 'requests>=0.13.1'],
    py_modules=['mailsnake'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
