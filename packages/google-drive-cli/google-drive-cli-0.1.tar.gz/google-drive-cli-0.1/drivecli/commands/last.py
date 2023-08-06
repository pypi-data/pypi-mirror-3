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

import pprint

from drivecli import utils
from drivecli.commands import base


class LastCommand(base.BaseCommand):
  """Access the raw data of the last returned valid response."""
  name = 'last'

  def Configure(self, parser):
    parser.add_argument('attributes', nargs='*', metavar='attr')

  def Execute(self, d, opts):
    val = self.boss.responses[-1]
    if not opts.attributes:
      pprint.pprint(val)
      return
    for attr in opts.attributes:
      try:
        val = utils.GetAttr(val, attr)
      except Exception, e:
        print e.__class__.__name__, e
        return
      pprint.pprint(val)
