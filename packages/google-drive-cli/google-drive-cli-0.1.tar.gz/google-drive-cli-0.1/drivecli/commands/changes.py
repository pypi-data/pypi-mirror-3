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


class ChangesCommand(base.BaseCommand):
  """Fetch the changes for a given file."""

  name = 'changes'

  def Configure(self, parser):
    parser.add_argument('-m', '--maxResults', type=int)
    parser.add_argument('-n', '--nextPage', action='store_true')
    parser.add_argument('-t', '--pageToken')

  def Execute(self, d, opts):
    args = {}
    if opts.maxResults:
      args['maxResults'] = opts.maxResults
    else:
      args['maxResults'] = 5
    if opts.pageToken:
      args['pageToken'] = opts.pageToken
    if opts.nextPage:
      args['pageToken'] = self.boss.responses[-1]['nextPageToken']
    r = drivelib._Changes(d, **args)
    if r == drivelib.Error:
      print r.status
      return
    items = r['items']
    for f in items:
      print self.FormatItem(f)
    return r

  def FormatItem(self, item):
    deleted = item['deleted'] and 'D' or ''
    if 'file' in item:
      modified = item['file']['modifiedDate'].split('T', 1)[0]
      title = item['file']['title']
    else:
      modified = mimeType = title = ''
    return '{0:<1} c{1:<6} {2:<10} {3} {4}'.format(
        deleted, item['id'], modified, item['fileId'] , title
    )
