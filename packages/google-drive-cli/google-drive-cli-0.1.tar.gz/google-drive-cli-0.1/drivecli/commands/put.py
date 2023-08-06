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

import os
import mimetypes

from drivecli import drivelib
from drivecli.commands import base


class PutCommand(base.BaseCommand):
  """Upload a file to Google Drive."""

  name = 'put'

  def Configure(self, parser):
    parser.add_argument('filename')
    parser.add_argument('-i', '--id')
    parser.add_argument('-f', '--folder')
    parser.add_argument('-m', '--mimeType')
    parser.add_argument('-t', '--title')

  def Execute(self, d, opts):
    filename = os.path.abspath(os.path.expanduser(opts.filename))
    if not os.path.exists(filename):
      print 'Local file does not exist [%s]' % filename
      return
    mimeType = opts.mimeType
    if not mimeType:
      t, e = mimetypes.guess_type(filename)
      if t is None:
        mimeType = 'application/octet-stream'
      else:
        mimeType = e
    title = opts.title or os.path.basename(filename)
    r = drivelib._Insert(d, filename=filename, mimeType=mimeType, title=title)
    if r == drivelib.Error:
      print r.status
      return
    print '[%s] uploaded' % opts.filename
    return r
