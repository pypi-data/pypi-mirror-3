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

import json

from drivecli import drivelib
from drivecli.commands import base


class AboutCommand(base.BaseCommand):
  """Reads the about feed to return user account information."""

  name = 'about'

  def Execute(self, d, opts):
    r = drivelib._About(d)
    if r == drivelib.Error:
      print r.status
    else:
      print json.dumps(r, indent=2)

      return r
