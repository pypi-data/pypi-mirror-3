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


class RecentCommand(base.BaseCommand):
  """Access the data for all responses in this session."""

  name = 'recent'

  def Configure(self, parser):
    """Configure

    Args:
      parser:
    """
    parser.add_argument('attributes', nargs='*', metavar='attr')

  def Execute(self, d, opts):
    """Execute

    Args:
      d:
      opts:
    """
    val = self.boss.responses
    if not opts.attributes:
      val = val[-1]
      pprint.pprint(val)
    for attr in opts.attributes:
      try:
        val = utils.GetAttr(val, attr)
      except Exception, e:
        print e.__class__.__name__, e
        return
      pprint.pprint(val)
