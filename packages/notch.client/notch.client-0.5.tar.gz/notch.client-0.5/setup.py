#!/usr/bin/env python
#
# Copyright 2010 Andrew Fort
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import setuptools

tests_require=['mox']

try:
    f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
    long_description = f.read()
except Exception:
    long_description = None


setuptools.setup(
    name='notch.client',
    version='0.5',
    description='The Notch Client Library',
    long_description=long_description,
    install_requires=['eventlet >= 0.9.6',
                      'jsonrpclib',
                      'PyYAML >= 3.0',
                      'setuptools',
                      ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='tests',
    url='http://bitbucket.org/enemesco/notch-client',
    author='Andrew Fort',
    author_email='andrew.fort+pypi@gmail.com',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: Console',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: POSIX',
                 'Programming Language :: Python :: 2.6',
                 'Topic :: System :: Networking :: Monitoring',
                 'Topic :: System :: Systems Administration',
                 ],
    packages=['notch', 'notch.client'],
    namespace_packages=['notch'],
    zip_safe=False,
    )
