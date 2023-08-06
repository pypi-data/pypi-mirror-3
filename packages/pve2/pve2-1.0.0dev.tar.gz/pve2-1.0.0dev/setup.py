#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pve2',
    description='A library for accessing the Proxmox 2 API.',
    long_description="""
    This is a simple library that lets you authorize to the Proxmox 2 API and
    call its methods easily. At the moment it doesn't include the schema and
    doesn't do any validation.
    """,
    version='1.0.0dev',
    license='MIT',
    author='Radomir Dopieralski',
    author_email='devel@sheep.art.pl',
    url='https://bitbucket.org/thesheep/pve2/',
    keywords='pve2 api proxmox2 proxmox',
    py_modules=['pve2'],
    install_requires=['distribute'],
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
