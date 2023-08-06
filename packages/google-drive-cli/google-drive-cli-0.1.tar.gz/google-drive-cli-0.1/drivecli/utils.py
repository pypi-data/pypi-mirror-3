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


def GetAttr(d, attr):
  parts = attr.split('.')
  val = d
  for part in parts:
    if isinstance(val, list):
      part = int(part)
    val = val[part]
  return val


def AddPagingArgs(parser):
  parser.add_argument('-m', '--maxResults', type=int)
  parser.add_argument('-n', '--nextPage', action='store_true')
  parser.add_argument('-t', '--pageToken')


def GetPagingArgs(opts, boss):
  args = {}
  if opts.maxResults:
    args['maxResults'] = opts.maxResults
  else:
    args['maxResults'] = 5
  if opts.pageToken:
    args['pageToken'] = opts.pageToken
  if opts.nextPage:
    # TODO (afshar) ffs, what
    args['pageToken'] = boss.responses[-1]['nextPageToken']
  return args
