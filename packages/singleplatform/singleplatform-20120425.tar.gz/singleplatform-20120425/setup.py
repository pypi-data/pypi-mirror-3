#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis

from setuptools import setup, find_packages

import singleplatform
version = str(singleplatform.__version__)

setup(
    name='singleplatform',
    version=version,
    author='Mike Lewis',
    author_email='mike@fondu.com',
    url='http://github.com/mLewisLogic/singleplatform',
    description='easy-as-pie SinglePlatform wrapper library',
    long_description=open('./README.txt', 'r').read(),
    download_url='http://github.com/mLewisLogic/singleplatform/tarball/master',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: MIT License',
        ],
    packages=find_packages(),
    install_requires=[
        'httplib2>=0.7',
        'poster>=0.8'
    ],
    license='MIT License',
    keywords='singleplatform api',
    include_package_data=True,
    zip_safe=True,
)
