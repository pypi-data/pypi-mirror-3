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
from drivecli import utils
from drivecli.commands import base


class LsCommand(base.BaseCommand):
  """List the contents of a Google Drive folder."""

  name = 'ls'

  def Configure(self, parser):
    parser.add_argument('folders', nargs='*', metavar='folder')
    utils.AddPagingArgs(parser)
    parser.add_argument('-q', '--query')
    parser.add_argument('-j', '--projection', choices=['BASIC', 'FULL'])

  def Execute(self, d, opts):
    args = utils.GetPagingArgs(opts, self.boss)
    if opts.query:
      args['q'] = opts.query
    if opts.projection:
      args['projection'] = opts.projection
    r = drivelib._List(d, **args)
    if r == drivelib.Error:
      print r.status
      return
    items = r['items']
    for f in items:
      print self.FormatItem(f)
    return r

  def FormatItem(self, item):
    if item['editable']:
      editable = 'w'
    else:
      editable = '-'
    modified = item['modifiedDate'].split('T', 1)[0]
    mimeType = item['mimeType'].replace('application/vnd.google-apps.', '')
    return '%s %s %s %s %s' % (
        editable, modified, item['id'], mimeType, item['title']
    )
