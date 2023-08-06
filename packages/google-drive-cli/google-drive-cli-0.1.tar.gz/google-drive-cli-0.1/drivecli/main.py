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

import os, logging
from drivecli import commands, drivelib, shell


# Set up logging
logging.basicConfig(filename=os.path.expanduser('~/.drivecli.log'),
                    level=logging.INFO, format='%(asctime)s %(msg)s', )


class Boss(object):
  """Application controller."""

  def __init__(self):
    self.cmd = shell.GenerateShell(commands.all_commands, self)
    self.debug = False
    self.http = drivelib.GetAuthorizedHttp(self)
    self.drive = drivelib.BuildClient(self.http)
    self.cfd = None
    self.cft = None
    self.responses = []

  def Log(self, msg):
    """Logs a message."""
    if self.debug:
      print msg
    logging.info(msg)

  def Start(self):
    """Starts the interactive shell."""
    self.cmd.cmdloop()


def Main():
  """Main entry point. Instantiate the application and start it."""
  b = Boss()
  b.Start()


if __name__ == '__main__':
  Main()
