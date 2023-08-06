# Copyright (C) 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Drive CLI, Installation script."""

__author__ = 'afshar@google.com (Ali Afshar)'

from setuptools import setup

setup(
    name = 'google-drive-cli',
    version = '0.1',
    author = 'Ali Afshar',
    author_email = 'afshar@google.com',
    packages = ['drivecli', 'drivecli.commands'],
    install_requires = ['google-api-python-client', 'argparse'],
    scripts = ['bin/drivecli'],
)
