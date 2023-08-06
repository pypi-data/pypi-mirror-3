#!/usr/bin/python

#       Copyright 2012, June.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from setuptools import setup
from os.path import abspath, join, dirname

if sys.version_info < (2,7):
    raise NotImplementedError("Sorry, Gates has only been tested on python 2.7 upwards")

setup(
    name="Gates",
    version="v1.0.0.beta",
    author="Iroiso Ikpokonte",
    author_email='iroiso@live.com',
    description="Minimal, fast and intuitive REST HTTP services in python",
    long_description=open(abspath(join(dirname(__file__), 'README.md'))).read(),
    maintainer='Iroiso Ikpokonte',
    maintainer_email='iroiso@live.com',
    package_dir = {'': 'src',},
    url="http://github.com/junery/gates",
    packages=["gates", "gates.core", ],
    provides=["gates"],
    install_requires =["webob==1.1.1", "routes==1.13"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
     ],
)
