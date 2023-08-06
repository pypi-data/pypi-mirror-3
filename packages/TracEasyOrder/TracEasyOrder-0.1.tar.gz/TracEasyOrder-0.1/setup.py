#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='TracEasyOrder',
    version='0.1',
    author='Erik Bray',
    author_email='erik.m.bray@gmail.com',
    description='Adds a nicer (JavaScript-based) UI for ordering enumerable '
                'ticket fields (severity, type, etc.) in Trac.',
    url='https://bitbucket.org/embray/tracext.easyorder',
    install_requires=['Trac>=0.12'],
    packages=['tracext', 'tracext.easyorder'],
    namespace_packages=['tracext'],
    package_data={'tracext.easyorder': ['htdocs/js/*.js']},
    entry_points={'trac.plugins': ['tracext.easyorder = tracext.easyorder']}
)
