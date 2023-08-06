#
# Copyright 2012, Couchbase, Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os
from setuptools import setup

here = os.path.dirname(os.path.abspath(__file__))
long_description = open(os.path.join(here, 'README.md')).read()

setup(
    name = "cbshell",
    version = "0.1",
    description = "Interactive python shell for couchbase",
    author = "Couchbase, Inc.",
    author_email = "info@couchbase.com",
    scripts = ['cbshell'],
    install_requires = ["httplib2", "requests==0.13.1",
                        "simplejson", "couchbase"],
    setup_requires = [],
    tests_require = [],
    url = "http://www.couchbase.com/",
    license = "LICENSE",
    keywords = ["encoding", "i18n", "xml"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = long_description,
)
