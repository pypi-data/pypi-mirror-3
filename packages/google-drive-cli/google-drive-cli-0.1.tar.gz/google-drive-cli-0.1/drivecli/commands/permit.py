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

__author__ = 'afshar@google.com (Ali Afshar)'

from drivecli import drivelib
from drivecli.commands import base


class PermitCommand(base.BaseCommand):
  """Add a permission to a file."""

  name = 'permit'

  def Configure(self, parser):
    parser.add_argument('-r', '--role', choices=['reader', 'writer', 'owner'],
                        required=True)
    parser.add_argument('-v', '--value', required=True)
    parser.add_argument('-t', '--type', choices=['user', 'group', 'domain',
                                                 'default'], required=True)
    parser.add_argument('file')

  def Execute(self, d, opts):
    r = drivelib._AddPermission(d, fileId=opts.file, role=opts.role,
                                type=opts.type, value=opts.value)
    if r == drivelib.Error:
      print r.status
    else:
      print r['role'], r['type']
      return r
