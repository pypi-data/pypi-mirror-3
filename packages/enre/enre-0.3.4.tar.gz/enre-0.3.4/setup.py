#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):

    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    except IOError:
        return ''

setup(
    name='enre',
    version=__import__('enre').__version__,
    packages=find_packages(exclude=['qxdemo', 'qxdemo.*']),
    url='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',

        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',

        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    install_requires=[],
    include_package_data=True,
    license='GPL',
    keywords='django qooxdoo',
    author='gratromv',
    author_email='gratromv@gmail.com',
    description=''
)
