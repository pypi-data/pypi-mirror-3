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

import argparse
import shlex


class BaseCommand(object):
  """Superclass containing common command behavior."""

  name = None


  def __init__(self):
    # Note without __new__ hackery, enforces name on the *class*
    if not self.name:
      raise NotImplementedError('Commands must define a name.')

  def Execute(self, d, r, opts):
    """Execute this command.

    This must be overriden in subclasses to provide actual functionality.
    """
    raise NotImplementedError

  def Configure(self, parser):
    """Configure the option parser.

    This may be overriden in subclasses to provide actual functionality.
    """
    pass

  def _Parse(self, line):
    self.args = shlex.split(line)
    parser = argparse.ArgumentParser(prog=self.name,
                                     description=self.__doc__.strip())
    parser.add_argument('--debug', action='store_true')
    self.Configure(parser)
    try:
      return parser.parse_args(self.args)
    except SystemExit:
      return None

  def _Execute(self, line):
    opts = self._Parse(line)
    if opts:
      r = self.Execute(self.boss.drive, self._Parse(line))
      if r:
        self.boss.responses.append(r)
      return r
