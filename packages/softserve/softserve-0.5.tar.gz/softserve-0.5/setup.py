#!/usr/bin/env python

# This file is subject to the terms and conditions defined in file
# 'LICENSE.txt', which is part of this source code package.

from distutils.core import setup

setup(
    name='softserve',
    version='0.5',
    description='A local web server with built-in delay',
    author='Eric Suh',
    author_email='contact@ericsuh.com',
    scripts=['softserve.py'],
    url='http://github.com/ericsuh/softserve',
    download_url='https://github.com/ericsuh/softserve/zipball/master',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development',
    ],

    long_description="""\
A local web serve with built-in delay
-------------------------------------

Use to serve local files with a simulated network delay; sounds strange,
but it can be useful for web app development when you need to see how
lag can affect rendering and user experience.

Compatible with both Python 2.7+ and Python 3.2+. Untested below those.
"""
)
