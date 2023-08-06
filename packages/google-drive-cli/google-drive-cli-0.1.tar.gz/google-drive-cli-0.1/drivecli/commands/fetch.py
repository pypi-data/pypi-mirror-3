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


class FetchCommand(base.BaseCommand):
  """Download a file's metadata and download the content."""

  name = 'fetch'

  def Configure(self, parser):
    parser.add_argument('fileId')
    parser.add_argument('-d', '--download', action='store_true')
    parser.add_argument('-f', '--downloadFilename')

  def Execute(self, d, opts):
    r = drivelib._Get(d, opts.fileId)
    if r == drivelib.Error:
      print r
    else:
      print r['title']
      if opts.download or opts.downloadFilename:
        uri = r.get('downloadUrl')
        print uri
        if uri:
          content = drivelib._DownloadFile(d, uri, opts.downloadFilename)
          print len(content)
        else:
          print 'This file is not downloadable.'


      return r
