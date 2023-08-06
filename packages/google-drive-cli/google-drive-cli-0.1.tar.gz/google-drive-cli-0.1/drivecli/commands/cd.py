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


class CdCommand(base.BaseCommand):
  """Change the current folder in Drive."""

  name = 'cd'

  def Configure(self, parser):
    parser.add_argument('folder')

  def Execute(self, d, opts):
    r = drivelib._Get(d, id=opts.folder)
    if r == drivelib.Error:
      print r.status
      return
    if r['mimeType'] != 'application/vnd.google-apps.folder':
      print '[%s] is not a folder' % r['title']
      return
    self.boss.cfd = opts.folder
    self.boss.cft = r['title']
    return r
